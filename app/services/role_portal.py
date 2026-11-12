from datetime import UTC, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from fastapi import Request, UploadFile
from fastapi.encoders import jsonable_encoder
from sqlalchemy import exists, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.exceptions import (
    AuthorizationException,
    BusinessRuleException,
    ConflictException,
    NotFoundException,
)
from app.core.transactions import transaction
from app.models.class_model import Class
from app.models.role_portal import (
    Assessment,
    AssessmentResult,
    Assignment,
    AssignmentAttachment,
    SchoolEvent,
    TimetableEntry,
)
from app.models.student import Student
from app.models.student_inquiry import StudentInquiry
from app.models.subject import ClassSubject, Subject, TeacherClassSubject
from app.models.teacher import Teacher, TeacherClass
from app.models.user import User
from app.repositories.subjects import active_teacher_exists
from app.schemas.role_portal import (
    AssessmentCreateRequest,
    AssessmentResultRequest,
    AssessmentUpdateRequest,
    AssignmentCreateRequest,
    AssignmentUpdateRequest,
    EventCreateRequest,
    EventReviewRequest,
    EventUpdateRequest,
    TimetableCreateRequest,
    TimetableUpdateRequest,
)
from app.services.audit import AuditService
from app.services.auth import _collect_roles_and_permissions
from app.utils.file_storage import save_upload_file

ADMIN_ROLES = {"ADMIN", "SUPER_ADMIN"}


def _database_utc(value: datetime) -> datetime:
    return value.astimezone(UTC).replace(tzinfo=None)


def _aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


class RolePortalService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.audit = AuditService(session)

    @staticmethod
    def roles(user: User) -> set[str]:
        roles, _ = _collect_roles_and_permissions(user)
        return set(roles)

    def _teacher(self, user: User, teacher_id: int | None = None) -> Teacher:
        roles = self.roles(user)
        if roles.intersection(ADMIN_ROLES):
            if teacher_id is None:
                raise BusinessRuleException("Select the teacher for this academic record")
            teacher = self.session.get(Teacher, teacher_id)
            if not teacher or teacher.status != "active":
                raise NotFoundException("Active teacher not found")
            return teacher
        if "TEACHER" in roles:
            teacher = self.session.scalar(select(Teacher).where(Teacher.user_id == user.id))
            if not teacher or teacher.status != "active":
                raise AuthorizationException("An active teacher profile is required")
            if teacher_id is not None and teacher_id != teacher.id:
                raise AuthorizationException("Teachers can only act for their own profile")
            return teacher
        raise AuthorizationException()

    def _linked_student_ids(self, user: User) -> list[int]:
        roles = self.roles(user)
        clauses = []
        if "STUDENT" in roles:
            clauses.append(Student.email == user.email)
        if "PARENT" in roles and user.phone:
            clauses.append(
                exists(
                    select(StudentInquiry.id).where(
                        StudentInquiry.id == Student.inquiry_id,
                        StudentInquiry.email == user.email,
                        StudentInquiry.parent_mobile == user.phone,
                    )
                )
            )
        if not clauses:
            return []
        return list(
            self.session.scalars(
                select(Student.id).where(
                    Student.deleted_at.is_(None),
                    or_(*clauses),
                )
            ).all()
        )

    def _student_classes(self, user: User) -> list[int]:
        student_ids = self._linked_student_ids(user)
        if not student_ids:
            return []
        return list(
            self.session.scalars(
                select(Student.class_id)
                .where(
                    Student.id.in_(student_ids),
                    Student.class_id.is_not(None),
                )
                .distinct()
            ).all()
        )

    def _require_class_subject(self, class_id: int, subject_id: int) -> None:
        offering = self.session.scalar(
            select(ClassSubject)
            .join(Class, Class.id == ClassSubject.class_id)
            .join(Subject, Subject.id == ClassSubject.subject_id)
            .where(
                ClassSubject.class_id == class_id,
                ClassSubject.subject_id == subject_id,
                ClassSubject.is_active.is_(True),
                Class.status == "active",
                Class.deleted_at.is_(None),
                Subject.is_active.is_(True),
            )
        )
        if not offering:
            raise BusinessRuleException("The selected subject is not offered to this active class")

    def _require_teacher_mapping(self, teacher_id: int, class_id: int, subject_id: int) -> None:
        if not active_teacher_exists(self.session, teacher_id):
            raise NotFoundException("Active teacher not found")
        assignment = self.session.get(TeacherClassSubject, (teacher_id, class_id, subject_id))
        if assignment is None or not assignment.is_active:
            raise BusinessRuleException(
                "The teacher must be mapped to the selected class and subject"
            )

    def list_own_teaching_assignments(self, user: User):
        teacher = self._teacher(user)
        return list(
            self.session.execute(
                select(
                    TeacherClassSubject.class_id,
                    TeacherClassSubject.subject_id,
                    Class.name,
                    Subject.name,
                )
                .join(Class, Class.id == TeacherClassSubject.class_id)
                .join(Subject, Subject.id == TeacherClassSubject.subject_id)
                .where(
                    TeacherClassSubject.teacher_id == teacher.id,
                    TeacherClassSubject.is_active.is_(True),
                    Class.status == "active",
                    Class.deleted_at.is_(None),
                    Subject.is_active.is_(True),
                )
                .order_by(Class.academic_year, Class.name, Subject.name)
            ).tuples()
        )

    def add_own_teaching_assignment(
        self,
        user: User,
        class_id: int,
        subject_id: int,
        request: Request,
    ) -> None:
        teacher = self._teacher(user)
        self._require_class_subject(class_id, subject_id)
        key = (teacher.id, class_id, subject_id)
        existing_assignment = self.session.get(TeacherClassSubject, key)
        if existing_assignment is not None and existing_assignment.is_active:
            raise ConflictException("Teacher is already assigned to this class subject")
        try:
            with transaction(self.session):
                if existing_assignment is not None:
                    existing_assignment.is_active = True
                else:
                    self.session.add(
                        TeacherClassSubject(
                            teacher_id=teacher.id,
                            class_id=class_id,
                            subject_id=subject_id,
                        )
                    )
                if self.session.get(TeacherClass, (teacher.id, class_id)) is None:
                    self.session.add(TeacherClass(teacher_id=teacher.id, class_id=class_id))
                self.audit.log(
                    action="teacher.self_class_subject.assign",
                    entity_type="teacher",
                    entity_id=teacher.id,
                    actor_user_id=user.id,
                    new_values={"class_id": class_id, "subject_id": subject_id},
                    request=request,
                )
        except IntegrityError as exc:
            raise ConflictException("Teacher is already assigned to this class subject") from exc

    def remove_own_teaching_assignment(
        self,
        user: User,
        class_id: int,
        subject_id: int,
        request: Request,
    ) -> None:
        teacher = self._teacher(user)
        assignment = self.session.get(
            TeacherClassSubject,
            (teacher.id, class_id, subject_id),
        )
        if assignment is None or not assignment.is_active:
            raise NotFoundException("Teacher is not assigned to this class subject")
        referenced = any(
            self.session.scalar(
                select(model.id).where(
                    model.teacher_id == teacher.id,
                    model.class_id == class_id,
                    model.subject_id == subject_id,
                )
            )
            is not None
            for model in (Assignment, TimetableEntry, Assessment)
        )
        if referenced:
            raise ConflictException(
                "This teaching mapping is in use by assignments, timetable, or assessments"
            )
        try:
            with transaction(self.session):
                assignment.is_active = False
                self.audit.log(
                    action="teacher.self_class_subject.remove",
                    entity_type="teacher",
                    entity_id=teacher.id,
                    actor_user_id=user.id,
                    old_values={"class_id": class_id, "subject_id": subject_id},
                    request=request,
                )
        except IntegrityError as exc:
            raise ConflictException("This teaching mapping is still in use") from exc

    def _assignment_query(self, user: User):
        roles = self.roles(user)
        stmt = select(Assignment).options(selectinload(Assignment.attachments))
        if roles.intersection(ADMIN_ROLES):
            return stmt
        if "TEACHER" in roles:
            teacher = self._teacher(user)
            return stmt.where(Assignment.assigned_teacher_id == teacher.id)
        class_ids = self._student_classes(user)
        if not class_ids:
            return stmt.where(False)
        return stmt.where(
            Assignment.class_id.in_(class_ids),
            Assignment.status == "published",
        )

    def list_assignments(self, user: User, class_id: int | None = None):
        stmt = self._assignment_query(user)
        if class_id is not None:
            stmt = stmt.where(Assignment.class_id == class_id)
        return list(self.session.scalars(stmt.order_by(Assignment.due_date, Assignment.id)).all())

    def get_assignment(self, assignment_id: int, user: User) -> Assignment:
        assignment = self.session.scalar(
            self._assignment_query(user).where(Assignment.id == assignment_id)
        )
        if not assignment:
            raise NotFoundException("Assignment not found")
        return assignment

    def create_assignment(
        self,
        payload: AssignmentCreateRequest,
        user: User,
        request: Request,
    ) -> Assignment:
        teacher_id = self._teacher(user, payload.teacher_id).id
        self._require_class_subject(payload.class_id, payload.subject_id)
        self._require_teacher_mapping(teacher_id, payload.class_id, payload.subject_id)
        school_today = datetime.now(ZoneInfo(get_settings().school_timezone)).date()
        if payload.due_date < (payload.assigned_date or school_today):
            raise BusinessRuleException("Due date cannot be before the assigned date")
        with transaction(self.session):
            assignment = Assignment(
                title=payload.title,
                details=payload.details,
                class_id=payload.class_id,
                subject_id=payload.subject_id,
                assigned_teacher_id=teacher_id,
                assigned_date=payload.assigned_date or school_today,
                due_date=payload.due_date,
                status="draft",
                created_by=user.id,
            )
            self.session.add(assignment)
            self.session.flush()
            self.audit.log(
                action="assignment.create",
                entity_type="assignment",
                entity_id=assignment.id,
                actor_user_id=user.id,
                new_values=jsonable_encoder(assignment, exclude={"attachments"}),
                request=request,
            )
            self.session.refresh(assignment)
            return assignment

    def update_assignment(
        self,
        assignment_id: int,
        payload: AssignmentUpdateRequest,
        user: User,
        request: Request,
    ) -> Assignment:
        assignment = self.get_assignment(assignment_id, user)
        if assignment.status != "draft":
            raise BusinessRuleException("Only draft assignments can be edited")
        values = payload.model_dump(exclude_unset=True)
        if not values or all(value is None for value in values.values()):
            raise BusinessRuleException("At least one assignment field must be provided")
        if values.get("due_date") and values["due_date"] < assignment.assigned_date:
            raise BusinessRuleException("Due date cannot be before the assigned date")
        before = {
            "title": assignment.title,
            "details": assignment.details,
            "due_date": assignment.due_date,
        }
        with transaction(self.session):
            for key, value in values.items():
                if value is not None:
                    setattr(assignment, key, value)
            assignment.updated_by = user.id
            self.session.flush()
            self.audit.log(
                action="assignment.update",
                entity_type="assignment",
                entity_id=assignment.id,
                actor_user_id=user.id,
                old_values=jsonable_encoder(before),
                new_values=jsonable_encoder(
                    {
                        "title": assignment.title,
                        "details": assignment.details,
                        "due_date": assignment.due_date,
                    }
                ),
                request=request,
            )
            self.session.refresh(assignment)
            return assignment

    def change_assignment_status(
        self,
        assignment_id: int,
        status_value: str,
        user: User,
        request: Request,
    ) -> Assignment:
        assignment = self.get_assignment(assignment_id, user)
        if assignment.status == "closed":
            raise BusinessRuleException("Closed assignments cannot be changed")
        if assignment.status == status_value:
            return assignment
        if status_value == "closed" and assignment.status != "published":
            raise BusinessRuleException("Only published assignments can be closed")
        with transaction(self.session):
            old_status = assignment.status
            assignment.status = status_value
            assignment.updated_by = user.id
            self.session.flush()
            self.audit.log(
                action=f"assignment.{status_value}",
                entity_type="assignment",
                entity_id=assignment.id,
                actor_user_id=user.id,
                old_values={"status": old_status},
                new_values={"status": status_value},
                request=request,
            )
            self.session.refresh(assignment)
            return assignment

    def upload_assignment_attachment(
        self,
        assignment_id: int,
        upload: UploadFile,
        user: User,
        request: Request,
    ) -> AssignmentAttachment:
        assignment = self.get_assignment(assignment_id, user)
        if assignment.status != "draft":
            raise BusinessRuleException("Attachments can only be added to draft assignments")
        relative_path, file_name = save_upload_file(upload, f"assignments/{assignment.id}")
        try:
            with transaction(self.session):
                attachment = AssignmentAttachment(
                    assignment_id=assignment.id,
                    file_name=file_name,
                    file_path=relative_path,
                    content_type=upload.content_type,
                    uploaded_by=user.id,
                )
                self.session.add(attachment)
                self.session.flush()
                self.audit.log(
                    action="assignment.attachment.upload",
                    entity_type="assignment",
                    entity_id=assignment.id,
                    actor_user_id=user.id,
                    new_values={
                        "attachment_id": attachment.id,
                        "file_name": attachment.file_name,
                    },
                    request=request,
                )
                self.session.refresh(attachment)
                return attachment
        except Exception:
            (get_settings().upload_path / relative_path).unlink(missing_ok=True)
            raise

    def get_assignment_attachment(
        self,
        assignment_id: int,
        attachment_id: int,
        user: User,
    ) -> tuple[AssignmentAttachment, Path]:
        assignment = self.get_assignment(assignment_id, user)
        attachment = self.session.scalar(
            select(AssignmentAttachment).where(
                AssignmentAttachment.id == attachment_id,
                AssignmentAttachment.assignment_id == assignment.id,
            )
        )
        if not attachment:
            raise NotFoundException("Assignment attachment not found")
        root = get_settings().upload_path.resolve()
        path = (root / attachment.file_path).resolve()
        if root not in path.parents or not path.is_file():
            raise NotFoundException("Assignment attachment file not found")
        return attachment, path

    def _timetable_query(self, user: User):
        roles = self.roles(user)
        stmt = select(TimetableEntry)
        if roles.intersection(ADMIN_ROLES):
            return stmt
        if "TEACHER" in roles:
            teacher = self._teacher(user)
            return stmt.where(TimetableEntry.teacher_id == teacher.id)
        class_ids = self._student_classes(user)
        return (
            stmt.where(TimetableEntry.class_id.in_(class_ids)) if class_ids else stmt.where(False)
        )

    def list_timetable(
        self, user: User, class_id: int | None = None, academic_year: str | None = None
    ):
        stmt = self._timetable_query(user)
        if class_id is not None:
            stmt = stmt.where(TimetableEntry.class_id == class_id)
        if academic_year:
            stmt = stmt.where(TimetableEntry.academic_year == academic_year)
        return list(
            self.session.scalars(
                stmt.order_by(TimetableEntry.day_of_week, TimetableEntry.start_time)
            ).all()
        )

    def _validate_timetable_conflicts(
        self,
        entry: TimetableEntry | None,
        *,
        class_id: int,
        teacher_id: int,
        day_of_week: int,
        start_time,
        end_time,
        academic_year: str,
    ) -> None:
        if start_time >= end_time:
            raise BusinessRuleException("End time must be later than start time")
        stmt = select(TimetableEntry).where(
            TimetableEntry.academic_year == academic_year,
            TimetableEntry.day_of_week == day_of_week,
            TimetableEntry.start_time < end_time,
            TimetableEntry.end_time > start_time,
            or_(
                TimetableEntry.class_id == class_id,
                TimetableEntry.teacher_id == teacher_id,
            ),
        )
        if entry:
            stmt = stmt.where(TimetableEntry.id != entry.id)
        conflicting = self.session.scalar(stmt)
        if conflicting:
            if conflicting.class_id == class_id:
                raise ConflictException("The class already has an overlapping timetable period")
            raise ConflictException("The teacher already has an overlapping timetable period")

    def _lock_timetable_scope(self, class_ids: set[int], teacher_ids: set[int]) -> None:
        for class_id in sorted(class_ids):
            self.session.scalar(select(Class.id).where(Class.id == class_id).with_for_update())
        for teacher_id in sorted(teacher_ids):
            self.session.scalar(
                select(Teacher.id).where(Teacher.id == teacher_id).with_for_update()
            )

    def create_timetable_entry(
        self,
        payload: TimetableCreateRequest,
        user: User,
        request: Request,
    ) -> TimetableEntry:
        teacher_id = self._teacher(user, payload.teacher_id).id
        with transaction(self.session):
            self._lock_timetable_scope({payload.class_id}, {teacher_id})
            self._require_class_subject(payload.class_id, payload.subject_id)
            self._require_teacher_mapping(teacher_id, payload.class_id, payload.subject_id)
            self._validate_timetable_conflicts(
                None,
                class_id=payload.class_id,
                teacher_id=teacher_id,
                day_of_week=payload.day_of_week,
                start_time=payload.start_time,
                end_time=payload.end_time,
                academic_year=payload.academic_year,
            )
            entry = TimetableEntry(
                class_id=payload.class_id,
                subject_id=payload.subject_id,
                teacher_id=teacher_id,
                day_of_week=payload.day_of_week,
                start_time=payload.start_time,
                end_time=payload.end_time,
                room=payload.room,
                academic_year=payload.academic_year,
                created_by=user.id,
            )
            self.session.add(entry)
            self.session.flush()
            self.audit.log(
                action="timetable.create",
                entity_type="timetable_entry",
                entity_id=entry.id,
                actor_user_id=user.id,
                new_values=jsonable_encoder(entry),
                request=request,
            )
            self.session.refresh(entry)
            return entry

    def update_timetable_entry(
        self,
        entry_id: int,
        payload: TimetableUpdateRequest,
        user: User,
        request: Request,
    ) -> TimetableEntry:
        initial_entry = self.session.get(TimetableEntry, entry_id)
        if not initial_entry:
            raise NotFoundException("Timetable entry not found")
        roles = self.roles(user)
        if "TEACHER" in roles and not roles.intersection(ADMIN_ROLES):
            teacher = self._teacher(user)
            if teacher.id != initial_entry.teacher_id:
                raise AuthorizationException()
        values = payload.model_dump(exclude_unset=True)
        if not values or all(value is None for value in values.values()):
            raise BusinessRuleException("At least one timetable field must be provided")
        with transaction(self.session):
            entry = self.session.scalar(
                select(TimetableEntry).where(TimetableEntry.id == entry_id).with_for_update()
            )
            if not entry:
                raise NotFoundException("Timetable entry not found")
            updated = {
                "class_id": values.get("class_id", entry.class_id),
                "subject_id": values.get("subject_id", entry.subject_id),
                "teacher_id": values.get("teacher_id", entry.teacher_id),
                "day_of_week": values.get("day_of_week", entry.day_of_week),
                "start_time": values.get("start_time", entry.start_time),
                "end_time": values.get("end_time", entry.end_time),
                "room": values.get("room", entry.room),
                "academic_year": values.get("academic_year", entry.academic_year),
            }
            teacher = self._teacher(user, updated["teacher_id"])
            updated["teacher_id"] = teacher.id
            self._lock_timetable_scope(
                {entry.class_id, updated["class_id"]},
                {entry.teacher_id, updated["teacher_id"]},
            )
            self._require_class_subject(updated["class_id"], updated["subject_id"])
            self._require_teacher_mapping(
                updated["teacher_id"], updated["class_id"], updated["subject_id"]
            )
            self._validate_timetable_conflicts(
                entry,
                class_id=updated["class_id"],
                teacher_id=updated["teacher_id"],
                day_of_week=updated["day_of_week"],
                start_time=updated["start_time"],
                end_time=updated["end_time"],
                academic_year=updated["academic_year"],
            )
            before = {key: getattr(entry, key) for key in updated}
            for key, value in updated.items():
                setattr(entry, key, value)
            entry.updated_by = user.id
            self.session.flush()
            self.audit.log(
                action="timetable.update",
                entity_type="timetable_entry",
                entity_id=entry.id,
                actor_user_id=user.id,
                old_values=jsonable_encoder(before),
                new_values=jsonable_encoder(updated),
                request=request,
            )
            self.session.refresh(entry)
            return entry

    def _assessment_query(self, user: User):
        roles = self.roles(user)
        stmt = select(Assessment).options(selectinload(Assessment.results))
        if roles.intersection(ADMIN_ROLES):
            return stmt
        if "TEACHER" in roles:
            teacher = self._teacher(user)
            return stmt.where(Assessment.teacher_id == teacher.id)
        class_ids = self._student_classes(user)
        if not class_ids:
            return stmt.where(False)
        return stmt.where(
            Assessment.class_id.in_(class_ids),
            Assessment.is_published.is_(True),
        )

    def visible_assessment_results(
        self,
        assessment: Assessment,
        user: User,
    ) -> list[AssessmentResult]:
        roles = self.roles(user)
        if roles.intersection(ADMIN_ROLES | {"TEACHER"}):
            return assessment.results
        student_ids = set(self._linked_student_ids(user))
        return [result for result in assessment.results if result.student_id in student_ids]

    def list_assessments(self, user: User, class_id: int | None = None):
        stmt = self._assessment_query(user)
        if class_id is not None:
            stmt = stmt.where(Assessment.class_id == class_id)
        assessments = self.session.scalars(
            stmt.order_by(Assessment.assessment_date.desc(), Assessment.id)
        ).all()
        return list(assessments)

    def get_assessment(self, assessment_id: int, user: User) -> Assessment:
        assessment = self.session.scalar(
            self._assessment_query(user).where(Assessment.id == assessment_id)
        )
        if not assessment:
            raise NotFoundException("Assessment not found")
        return assessment

    def create_assessment(
        self,
        payload: AssessmentCreateRequest,
        user: User,
        request: Request,
    ) -> Assessment:
        teacher_id = self._teacher(user, payload.teacher_id).id
        self._require_class_subject(payload.class_id, payload.subject_id)
        self._require_teacher_mapping(teacher_id, payload.class_id, payload.subject_id)
        with transaction(self.session):
            assessment = Assessment(
                name=payload.name,
                assessment_type=payload.assessment_type,
                class_id=payload.class_id,
                subject_id=payload.subject_id,
                teacher_id=teacher_id,
                assessment_date=payload.assessment_date,
                max_score=payload.max_score,
                is_published=False,
                created_by=user.id,
            )
            self.session.add(assessment)
            self.session.flush()
            self.audit.log(
                action="assessment.create",
                entity_type="assessment",
                entity_id=assessment.id,
                actor_user_id=user.id,
                new_values=jsonable_encoder(assessment, exclude={"results"}),
                request=request,
            )
            self.session.refresh(assessment)
            return assessment

    def update_assessment(
        self,
        assessment_id: int,
        payload: AssessmentUpdateRequest,
        user: User,
        request: Request,
    ) -> Assessment:
        self.get_assessment(assessment_id, user)
        values = payload.model_dump(exclude_unset=True)
        if not values or all(value is None for value in values.values()):
            raise BusinessRuleException("At least one assessment field must be provided")
        with transaction(self.session):
            assessment = self.session.scalar(
                select(Assessment).where(Assessment.id == assessment_id).with_for_update()
            )
            if not assessment:
                raise NotFoundException("Assessment not found")
            if assessment.is_published:
                raise BusinessRuleException("Published assessments cannot be edited")
            if values.get("max_score") is not None:
                highest_score = self.session.scalar(
                    select(AssessmentResult.score)
                    .where(
                        AssessmentResult.assessment_id == assessment.id,
                        AssessmentResult.score > values["max_score"],
                    )
                    .limit(1)
                )
                if highest_score is not None:
                    raise BusinessRuleException("Maximum score cannot be below an entered result")
            before = {key: getattr(assessment, key) for key in values}
            for key, value in values.items():
                if value is not None:
                    setattr(assessment, key, value)
            assessment.updated_by = user.id
            self.session.flush()
            self.audit.log(
                action="assessment.update",
                entity_type="assessment",
                entity_id=assessment.id,
                actor_user_id=user.id,
                old_values=jsonable_encoder(before),
                new_values=jsonable_encoder(values),
                request=request,
            )
            self.session.refresh(assessment)
            return assessment

    def upsert_assessment_result(
        self,
        assessment_id: int,
        student_id: int,
        payload: AssessmentResultRequest,
        user: User,
        request: Request,
    ) -> AssessmentResult:
        self.get_assessment(assessment_id, user)
        with transaction(self.session):
            assessment = self.session.scalar(
                select(Assessment).where(Assessment.id == assessment_id).with_for_update()
            )
            if not assessment:
                raise NotFoundException("Assessment not found")
            if assessment.is_published:
                raise BusinessRuleException("Results cannot be changed after publication")
            student = self.session.scalar(
                select(Student).where(
                    Student.id == student_id,
                    Student.class_id == assessment.class_id,
                    Student.deleted_at.is_(None),
                )
            )
            if not student:
                raise NotFoundException("Active student in this assessment class not found")
            if payload.score is not None and payload.score > assessment.max_score:
                raise BusinessRuleException("Student score cannot exceed the assessment maximum")
            result = self.session.scalar(
                select(AssessmentResult)
                .where(
                    AssessmentResult.assessment_id == assessment.id,
                    AssessmentResult.student_id == student_id,
                )
                .with_for_update()
            )
            before = (
                {
                    "score": result.score,
                    "result_status": result.result_status,
                    "remarks": result.remarks,
                }
                if result
                else None
            )
            if result is None:
                result = AssessmentResult(
                    assessment_id=assessment.id,
                    student_id=student.id,
                    entered_by=user.id,
                    **payload.model_dump(),
                )
                self.session.add(result)
            else:
                result.score = payload.score
                result.result_status = payload.result_status
                result.remarks = payload.remarks
                result.updated_by = user.id
            self.session.flush()
            self.audit.log(
                action="assessment.result.upsert",
                entity_type="assessment_result",
                entity_id=result.id,
                actor_user_id=user.id,
                old_values=jsonable_encoder(before),
                new_values=jsonable_encoder(
                    {
                        "assessment_id": assessment.id,
                        "student_id": student.id,
                        **payload.model_dump(),
                    }
                ),
                request=request,
            )
            self.session.refresh(result)
            return result

    def publish_assessment(
        self,
        assessment_id: int,
        user: User,
        request: Request,
    ) -> Assessment:
        self.get_assessment(assessment_id, user)
        with transaction(self.session):
            assessment = self.session.scalar(
                select(Assessment).where(Assessment.id == assessment_id).with_for_update()
            )
            if not assessment:
                raise NotFoundException("Assessment not found")
            if assessment.is_published:
                return assessment
            assessment.is_published = True
            assessment.updated_by = user.id
            self.session.flush()
            self.audit.log(
                action="assessment.publish",
                entity_type="assessment",
                entity_id=assessment.id,
                actor_user_id=user.id,
                old_values={"is_published": False},
                new_values={"is_published": True},
                request=request,
            )
            self.session.refresh(assessment)
            return assessment

    def _event_query(self, user: User):
        roles = self.roles(user)
        stmt = select(SchoolEvent)
        if roles.intersection(ADMIN_ROLES):
            return stmt
        if "TEACHER" in roles:
            return stmt.where(
                or_(
                    SchoolEvent.created_by == user.id,
                    SchoolEvent.status == "published",
                )
            )
        audience = ["public", "all"]
        if "STUDENT" in roles:
            audience.append("students")
        if "PARENT" in roles:
            audience.append("parents")
        return stmt.where(
            SchoolEvent.status == "published",
            SchoolEvent.audience.in_(audience),
        )

    def list_events(self, user: User):
        return list(
            self.session.scalars(
                self._event_query(user).order_by(SchoolEvent.starts_at, SchoolEvent.id)
            ).all()
        )

    def list_public_events(self):
        return list(
            self.session.scalars(
                select(SchoolEvent)
                .where(
                    SchoolEvent.status == "published",
                    SchoolEvent.audience.in_(["public", "all"]),
                )
                .order_by(SchoolEvent.starts_at, SchoolEvent.id)
            ).all()
        )

    def create_event(
        self,
        payload: EventCreateRequest,
        user: User,
        request: Request,
    ) -> SchoolEvent:
        is_admin = bool(self.roles(user).intersection(ADMIN_ROLES))
        event_values = payload.model_dump()
        event_values["starts_at"] = _database_utc(payload.starts_at)
        event_values["ends_at"] = _database_utc(payload.ends_at)
        reviewed_at = datetime.now(UTC) if is_admin else None
        with transaction(self.session):
            event = SchoolEvent(
                **event_values,
                status="published" if is_admin else "pending_review",
                created_by=user.id,
                reviewed_by=user.id if is_admin else None,
                reviewed_at=_database_utc(reviewed_at) if reviewed_at else None,
            )
            self.session.add(event)
            self.session.flush()
            self.audit.log(
                action="event.create",
                entity_type="school_event",
                entity_id=event.id,
                actor_user_id=user.id,
                new_values=jsonable_encoder(
                    {
                        **payload.model_dump(),
                        "status": event.status,
                        "created_by": user.id,
                        "reviewed_by": event.reviewed_by,
                        "reviewed_at": reviewed_at,
                    }
                ),
                request=request,
            )
            self.session.refresh(event)
            return event

    def update_event(
        self,
        event_id: int,
        payload: EventUpdateRequest,
        user: User,
        request: Request,
    ) -> SchoolEvent:
        event = self.session.get(SchoolEvent, event_id)
        if not event:
            raise NotFoundException("Event not found")
        roles = self.roles(user)
        is_admin = bool(roles.intersection(ADMIN_ROLES))
        if not is_admin:
            if "TEACHER" not in roles or event.created_by != user.id:
                raise AuthorizationException()
            if event.status not in {"pending_review", "published"}:
                raise BusinessRuleException("Rejected events cannot be edited")
        values = payload.model_dump(exclude_unset=True)
        if not values or all(value is None for value in values.values()):
            raise BusinessRuleException("At least one event field must be provided")
        updated = {
            key: value if value is not None else getattr(event, key)
            for key, value in values.items()
        }
        starts_at = _aware_utc(updated.get("starts_at", event.starts_at))
        ends_at = _aware_utc(updated.get("ends_at", event.ends_at))
        if starts_at >= ends_at:
            raise BusinessRuleException("Event end must be later than its start")
        for key in ("starts_at", "ends_at"):
            value = updated.get(key)
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise BusinessRuleException("Event date-times must include a timezone offset")
        before = {
            key: _aware_utc(getattr(event, key))
            if key in {"starts_at", "ends_at"}
            else getattr(event, key)
            for key in updated
        }
        with transaction(self.session):
            for key, value in updated.items():
                setattr(event, key, value)
                if key in {"starts_at", "ends_at"}:
                    setattr(event, key, _database_utc(value))
            if not is_admin and event.status == "published":
                event.status = "pending_review"
                event.reviewed_by = None
                event.reviewed_at = None
            self.session.flush()
            new_values = {key: updated.get(key, getattr(event, key)) for key in updated}
            new_values["status"] = event.status
            self.audit.log(
                action="event.update",
                entity_type="school_event",
                entity_id=event.id,
                actor_user_id=user.id,
                old_values=jsonable_encoder(before),
                new_values=jsonable_encoder(new_values),
                request=request,
            )
            self.session.refresh(event)
            return event

    def review_event(
        self,
        event_id: int,
        payload: EventReviewRequest,
        user: User,
        request: Request,
    ) -> SchoolEvent:
        event = self.session.get(SchoolEvent, event_id)
        if not event:
            raise NotFoundException("Event not found")
        if event.status != "pending_review":
            raise BusinessRuleException("Only events pending review can be approved or rejected")
        with transaction(self.session):
            previous = event.status
            event.status = payload.status
            event.reviewed_by = user.id
            reviewed_at = datetime.now(UTC)
            event.reviewed_at = _database_utc(reviewed_at)
            event.rejection_reason = (
                payload.rejection_reason.strip()
                if payload.status == "rejected" and payload.rejection_reason
                else None
            )
            self.session.flush()
            self.audit.log(
                action=f"event.{payload.status}",
                entity_type="school_event",
                entity_id=event.id,
                actor_user_id=user.id,
                old_values={"status": previous},
                new_values=jsonable_encoder(
                    {
                        "status": event.status,
                        "rejection_reason": event.rejection_reason,
                        "reviewed_at": reviewed_at,
                    }
                ),
                request=request,
            )
            self.session.refresh(event)
            return event
