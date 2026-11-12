from decimal import ROUND_HALF_UP, Decimal

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import (
    BusinessRuleException,
    ConflictException,
    NotFoundException,
    ValidationException,
)
from app.core.transactions import transaction
from app.models.academics import (
    Examination,
    ExaminationComponent,
    ExaminationResult,
    ExaminationSubject,
    GradingRule,
    StudentMark,
    StudentSubjectSelection,
)
from app.models.class_model import Class
from app.models.enums import ClassStatus, StudentStatus
from app.models.student import Student
from app.models.subject import ClassSubject, Subject, TeacherClassSubject
from app.models.teacher import Teacher
from app.models.user import User
from app.schemas.academics import (
    ExaminationCreateRequest,
    GradingScaleUpdateRequest,
    MarksBatchRequest,
    MarksCorrectionRequest,
    SubjectOfferingRequest,
)
from app.services.audit import AuditService

CENT = Decimal("0.01")


class AcademicService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.audit = AuditService(session)

    def list_offerings(self, class_id: int) -> list[dict]:
        school_class = self._get_class(class_id)
        rows = self.session.execute(
            select(ClassSubject, Subject)
            .join(Subject, Subject.id == ClassSubject.subject_id)
            .where(ClassSubject.class_id == school_class.id)
            .order_by(Subject.name)
        ).all()
        teacher_rows = self.session.execute(
            select(TeacherClassSubject, Teacher)
            .join(Teacher, Teacher.id == TeacherClassSubject.teacher_id)
            .where(
                TeacherClassSubject.class_id == school_class.id,
                TeacherClassSubject.is_active.is_(True),
                Teacher.status == "active",
            )
        ).all()
        teacher_by_subject = {
            assignment.subject_id: teacher for assignment, teacher in teacher_rows
        }
        return [
            {
                "class_id": school_class.id,
                "class_name": school_class.name,
                "section": school_class.section,
                "academic_year": school_class.academic_year,
                "subject_id": offering.subject_id,
                "code": subject.code,
                "name": subject.name,
                "category": subject.category,
                "subject_type": offering.subject_type,
                "stream": offering.stream,
                "is_active": offering.is_active and subject.is_active,
                "teacher_id": (
                    teacher_by_subject[offering.subject_id].id
                    if offering.subject_id in teacher_by_subject
                    else None
                ),
                "teacher_name": (
                    f"{teacher_by_subject[offering.subject_id].first_name} "
                    f"{teacher_by_subject[offering.subject_id].last_name}"
                    if offering.subject_id in teacher_by_subject
                    else None
                ),
            }
            for offering, subject in rows
        ]

    def configure_offering(
        self,
        class_id: int,
        subject_id: int,
        payload: SubjectOfferingRequest,
        actor_id: int,
        request: Request,
    ) -> dict:
        school_class = self._get_class(class_id)
        subject = self.session.get(Subject, subject_id)
        if not subject or not subject.is_active:
            raise NotFoundException("Active subject not found")
        offering = self.session.get(ClassSubject, (school_class.id, subject_id))
        if offering and offering.subject_type != payload.subject_type:
            has_exam = self.session.scalar(
                select(ExaminationSubject.id)
                .join(Examination)
                .where(
                    ExaminationSubject.class_id == class_id,
                    ExaminationSubject.subject_id == subject_id,
                )
                .limit(1)
            )
            if has_exam:
                raise ConflictException(
                    "Subject type cannot change after it has been added to an examination"
                )
        with transaction(self.session):
            if offering is None:
                offering = ClassSubject(
                    class_id=class_id,
                    subject_id=subject_id,
                    subject_type=payload.subject_type,
                    stream=payload.stream,
                    is_active=payload.is_active,
                )
                self.session.add(offering)
            else:
                offering.subject_type = payload.subject_type
                offering.stream = payload.stream
                offering.is_active = payload.is_active
            self.audit.log(
                action="academics.offering.configure",
                entity_type="class_subject",
                entity_id=subject_id,
                actor_user_id=actor_id,
                new_values={
                    "class_id": class_id,
                    "subject_id": subject_id,
                    "subject_type": payload.subject_type,
                    "stream": payload.stream,
                    "is_active": payload.is_active,
                },
                request=request,
            )
        return {
            "class_id": class_id,
            "subject_id": subject_id,
            "subject_type": offering.subject_type,
            "stream": offering.stream,
            "is_active": offering.is_active,
        }

    def assign_teacher(
        self,
        class_id: int,
        subject_id: int,
        teacher_id: int,
        actor_id: int,
        request: Request,
    ) -> dict:
        teacher = self.session.get(Teacher, teacher_id)
        if not teacher or teacher.status != "active":
            raise NotFoundException("Active teacher not found")
        with transaction(self.session):
            offering = self.session.scalar(
                select(ClassSubject)
                .where(
                    ClassSubject.class_id == class_id,
                    ClassSubject.subject_id == subject_id,
                    ClassSubject.is_active.is_(True),
                )
                .with_for_update()
            )
            if not offering:
                raise NotFoundException("Active class subject offering not found")
            assignments = self.session.scalars(
                select(TeacherClassSubject).where(
                    TeacherClassSubject.class_id == class_id,
                    TeacherClassSubject.subject_id == subject_id,
                )
            ).all()
            for assignment in assignments:
                assignment.is_active = assignment.teacher_id == teacher_id
            selected = next(
                (assignment for assignment in assignments if assignment.teacher_id == teacher_id),
                None,
            )
            if selected is None:
                selected = TeacherClassSubject(
                    teacher_id=teacher_id,
                    class_id=class_id,
                    subject_id=subject_id,
                    is_active=True,
                )
                self.session.add(selected)
            self.audit.log(
                action="academics.teacher.assign",
                entity_type="class_subject",
                entity_id=subject_id,
                actor_user_id=actor_id,
                new_values={
                    "class_id": class_id,
                    "subject_id": subject_id,
                    "teacher_id": teacher_id,
                },
                request=request,
            )
        return {
            "class_id": class_id,
            "subject_id": subject_id,
            "teacher_id": teacher_id,
            "teacher_name": f"{teacher.first_name} {teacher.last_name}",
        }

    def list_subject_selections(self, student_id: int) -> list[dict]:
        student = self._get_student(student_id)
        if not student.class_id:
            raise BusinessRuleException("Student is not assigned to a class")
        rows = self.session.execute(
            select(ClassSubject, Subject, StudentSubjectSelection)
            .join(Subject, Subject.id == ClassSubject.subject_id)
            .outerjoin(
                StudentSubjectSelection,
                (StudentSubjectSelection.class_id == ClassSubject.class_id)
                & (StudentSubjectSelection.subject_id == ClassSubject.subject_id)
                & (StudentSubjectSelection.student_id == student.id)
                & StudentSubjectSelection.is_active.is_(True),
            )
            .where(
                ClassSubject.class_id == student.class_id,
                ClassSubject.is_active.is_(True),
                Subject.is_active.is_(True),
            )
            .order_by(Subject.name)
        ).all()
        return [
            {
                "student_id": student.id,
                "subject_id": offering.subject_id,
                "code": subject.code,
                "name": subject.name,
                "subject_type": offering.subject_type,
                "stream": offering.stream,
                "selected": selection is not None
                if offering.subject_type in ("elective", "optional")
                else True,
            }
            for offering, subject, selection in rows
        ]

    def set_student_electives(
        self,
        student_id: int,
        subject_ids: list[int],
        actor_id: int,
        request: Request,
    ) -> list[dict]:
        student = self._get_student(student_id)
        if not student.class_id:
            raise BusinessRuleException("Student is not assigned to a class")
        if student.status != StudentStatus.ACTIVE.value:
            raise BusinessRuleException("Electives can only be assigned to an active student")
        if len(subject_ids) != len(set(subject_ids)):
            raise ValidationException("Each elective may only be selected once")
        offerings = self.session.scalars(
            select(ClassSubject)
            .join(Subject, Subject.id == ClassSubject.subject_id)
            .where(
                ClassSubject.class_id == student.class_id,
                ClassSubject.subject_id.in_(subject_ids or [-1]),
                ClassSubject.is_active.is_(True),
                ClassSubject.subject_type.in_(("elective", "optional")),
                Subject.is_active.is_(True),
            )
        ).all()
        if len(offerings) != len(subject_ids):
            raise ValidationException(
                "Selections must be active elective or optional subjects offered "
                "to the student's class"
            )
        with transaction(self.session):
            existing = self.session.scalars(
                select(StudentSubjectSelection).where(
                    StudentSubjectSelection.student_id == student_id,
                    StudentSubjectSelection.class_id == student.class_id,
                )
            ).all()
            selected = set(subject_ids)
            for selection in existing:
                selection.is_active = selection.subject_id in selected
            existing_ids = {selection.subject_id for selection in existing}
            for subject_id in selected - existing_ids:
                self.session.add(
                    StudentSubjectSelection(
                        student_id=student_id,
                        class_id=student.class_id,
                        subject_id=subject_id,
                        selected_by=actor_id,
                    )
                )
            self.audit.log(
                action="academics.electives.update",
                entity_type="student",
                entity_id=student_id,
                actor_user_id=actor_id,
                new_values={"class_id": student.class_id, "subject_ids": sorted(selected)},
                request=request,
            )
        return self.list_subject_selections(student_id)

    def create_examination(
        self,
        payload: ExaminationCreateRequest,
        actor_id: int,
        request: Request,
    ) -> Examination:
        school_class = self._get_class(payload.class_id)
        if self.session.scalar(
            select(Examination.id).where(
                Examination.class_id == payload.class_id,
                Examination.name == payload.name,
            )
        ):
            raise ConflictException("An examination with this name already exists for the class")
        subject_ids = [item.subject_id for item in payload.subjects]
        offerings = self.session.scalars(
            select(ClassSubject)
            .join(Subject, Subject.id == ClassSubject.subject_id)
            .where(
                ClassSubject.class_id == school_class.id,
                ClassSubject.subject_id.in_(subject_ids),
                ClassSubject.is_active.is_(True),
                Subject.is_active.is_(True),
            )
        ).all()
        if len(offerings) != len(subject_ids):
            raise ValidationException(
                "Every examination subject must be actively offered to the class"
            )
        required_ids = {
            offering.subject_id
            for offering in self.session.scalars(
                select(ClassSubject)
                .join(Subject, Subject.id == ClassSubject.subject_id)
                .where(
                    ClassSubject.class_id == school_class.id,
                    ClassSubject.subject_type == "mandatory",
                    ClassSubject.is_active.is_(True),
                    Subject.is_active.is_(True),
                )
            ).all()
        }
        if not required_ids.issubset(set(subject_ids)):
            raise ValidationException("All mandatory class subjects must be included")

        with transaction(self.session):
            examination = Examination(
                name=payload.name,
                class_id=school_class.id,
                examination_type=payload.examination_type,
                start_date=payload.start_date,
                end_date=payload.end_date,
                description=payload.description,
                status="draft",
                created_by=actor_id,
            )
            self.session.add(examination)
            self.session.flush()
            for subject_input in payload.subjects:
                if subject_input.teacher_id is not None:
                    assignment = self.session.get(
                        TeacherClassSubject,
                        (subject_input.teacher_id, school_class.id, subject_input.subject_id),
                    )
                    if not assignment or not assignment.is_active:
                        raise ValidationException(
                            "Selected teacher is not assigned to this active class subject"
                        )
                exam_subject = ExaminationSubject(
                    examination_id=examination.id,
                    class_id=school_class.id,
                    subject_id=subject_input.subject_id,
                    teacher_id=subject_input.teacher_id,
                    max_marks=subject_input.max_marks,
                    passing_marks=subject_input.passing_marks,
                )
                exam_subject.components = [
                    ExaminationComponent(
                        name=component.name,
                        component_type=component.component_type,
                        max_marks=component.max_marks,
                        passing_marks=component.passing_marks,
                    )
                    for component in subject_input.components
                ]
                examination.subjects.append(exam_subject)
            self.audit.log(
                action="academics.examination.create",
                entity_type="examination",
                entity_id=examination.id,
                actor_user_id=actor_id,
                new_values={
                    "class_id": school_class.id,
                    "name": payload.name,
                    "subject_ids": subject_ids,
                },
                request=request,
            )
        return self.get_examination(examination.id)

    def list_examinations(self, class_id: int | None = None) -> list[Examination]:
        query = select(Examination).options(
            selectinload(Examination.subjects).selectinload(ExaminationSubject.components)
        )
        if class_id is not None:
            query = query.where(Examination.class_id == class_id)
        return list(self.session.scalars(query.order_by(Examination.start_date.desc())).all())

    def get_examination(self, examination_id: int) -> Examination:
        examination = self.session.scalar(
            select(Examination)
            .options(selectinload(Examination.subjects).selectinload(ExaminationSubject.components))
            .where(Examination.id == examination_id)
        )
        if not examination:
            raise NotFoundException("Examination not found")
        return examination

    def schedule_examination(
        self,
        examination_id: int,
        actor_id: int,
        request: Request,
    ) -> Examination:
        examination = self.get_examination(examination_id)
        if examination.status != "draft":
            raise BusinessRuleException("Only a draft examination can be scheduled")
        with transaction(self.session):
            examination.status = "scheduled"
            examination.updated_by = actor_id
            self.audit.log(
                action="academics.examination.schedule",
                entity_type="examination",
                entity_id=examination.id,
                actor_user_id=actor_id,
                request=request,
            )
        return self.get_examination(examination_id)

    def enter_marks(
        self,
        examination_id: int,
        payload: MarksBatchRequest,
        actor_id: int,
        request: Request,
    ) -> dict:
        examination = self.get_examination(examination_id)
        if examination.status != "scheduled":
            raise BusinessRuleException("Marks can only be entered for a scheduled examination")
        with transaction(self.session):
            self._save_marks(examination, payload.marks, actor_id)
            self.audit.log(
                action="academics.marks.enter",
                entity_type="examination",
                entity_id=examination.id,
                actor_user_id=actor_id,
                new_values={"mark_count": len(payload.marks)},
                request=request,
            )
        return {"examination_id": examination_id, "saved_count": len(payload.marks)}

    def correct_marks(
        self,
        examination_id: int,
        payload: MarksCorrectionRequest,
        actor_id: int,
        request: Request,
    ) -> dict:
        examination = self.get_examination(examination_id)
        if examination.status not in ("published", "locked"):
            raise BusinessRuleException("Only published examination marks can be corrected")
        with transaction(self.session):
            self._save_marks(examination, payload.marks, actor_id)
            self._calculate_results(examination)
            self.audit.log(
                action="academics.marks.correct",
                entity_type="examination",
                entity_id=examination.id,
                actor_user_id=actor_id,
                new_values={
                    "mark_count": len(payload.marks),
                    "reason": payload.reason,
                },
                request=request,
            )
        return {"examination_id": examination_id, "corrected_count": len(payload.marks)}

    def publish_examination(
        self,
        examination_id: int,
        actor_id: int,
        request: Request,
    ) -> Examination:
        examination = self.get_examination(examination_id)
        if examination.status != "scheduled":
            raise BusinessRuleException("Only a scheduled examination can be published")
        with transaction(self.session):
            self._calculate_results(examination)
            examination.status = "published"
            examination.updated_by = actor_id
            self.audit.log(
                action="academics.examination.publish",
                entity_type="examination",
                entity_id=examination.id,
                actor_user_id=actor_id,
                request=request,
            )
        return self.get_examination(examination_id)

    def lock_examination(
        self,
        examination_id: int,
        actor_id: int,
        request: Request,
    ) -> Examination:
        examination = self.get_examination(examination_id)
        if examination.status != "published":
            raise BusinessRuleException("Only a published examination can be locked")
        with transaction(self.session):
            examination.status = "locked"
            examination.updated_by = actor_id
            self.audit.log(
                action="academics.examination.lock",
                entity_type="examination",
                entity_id=examination.id,
                actor_user_id=actor_id,
                request=request,
            )
        return self.get_examination(examination_id)

    def list_results(self, examination_id: int) -> list[dict]:
        examination = self.get_examination(examination_id)
        if examination.status not in ("published", "locked"):
            raise BusinessRuleException("Examination results are not published")
        results = self.session.scalars(
            select(ExaminationResult)
            .where(ExaminationResult.examination_id == examination_id)
            .order_by(ExaminationResult.student_id)
        ).all()
        return [
            {
                "student_id": result.student_id,
                "total_max_marks": result.total_max_marks,
                "total_obtained_marks": result.total_obtained_marks,
                "percentage": result.percentage,
                "grade": result.grade,
                "status": result.result_status,
            }
            for result in results
        ]

    def examination_roster(self, examination_id: int) -> list[dict]:
        examination = self.get_examination(examination_id)
        students = self.session.scalars(
            select(Student)
            .where(
                Student.class_id == examination.class_id,
                Student.status == StudentStatus.ACTIVE.value,
                Student.deleted_at.is_(None),
            )
            .order_by(Student.roll_number, Student.first_name, Student.id)
        ).all()
        component_ids = [
            component.id for subject in examination.subjects for component in subject.components
        ]
        existing_marks = self.session.scalars(
            select(StudentMark).where(
                StudentMark.student_id.in_([student.id for student in students] or [-1]),
                StudentMark.component_id.in_(component_ids or [-1]),
            )
        ).all()
        mark_by_key = {(mark.student_id, mark.component_id): mark for mark in existing_marks}
        data = []
        for student in students:
            subjects = []
            for exam_subject in examination.subjects:
                if not self._student_is_eligible_for_subject(student.id, exam_subject):
                    continue
                subject = self.session.get(Subject, exam_subject.subject_id)
                subjects.append(
                    {
                        "subject_id": exam_subject.subject_id,
                        "subject_name": subject.name if subject else "",
                        "components": [
                            {
                                "id": component.id,
                                "name": component.name,
                                "max_marks": component.max_marks,
                                "passing_marks": component.passing_marks,
                                "obtained_marks": (
                                    mark_by_key[(student.id, component.id)].obtained_marks
                                    if (student.id, component.id) in mark_by_key
                                    else None
                                ),
                                "status": (
                                    mark_by_key[(student.id, component.id)].result_status
                                    if (student.id, component.id) in mark_by_key
                                    else None
                                ),
                                "remarks": (
                                    mark_by_key[(student.id, component.id)].remarks
                                    if (student.id, component.id) in mark_by_key
                                    else None
                                ),
                            }
                            for component in exam_subject.components
                        ],
                    }
                )
            data.append(
                {
                    "student_id": student.id,
                    "student_code": student.student_code,
                    "student_name": f"{student.first_name} {student.last_name}",
                    "roll_number": student.roll_number,
                    "subjects": subjects,
                }
            )
        return data

    def student_subjects(self, current_user: User) -> list[dict]:
        student = self._student_for_user(current_user)
        return self.list_subject_selections(student.id)

    def student_results(self, current_user: User) -> list[dict]:
        student = self._student_for_user(current_user)
        results = self.session.execute(
            select(ExaminationResult, Examination)
            .join(Examination, Examination.id == ExaminationResult.examination_id)
            .where(
                ExaminationResult.student_id == student.id,
                Examination.status.in_(("published", "locked")),
            )
            .order_by(Examination.start_date.desc())
        ).all()
        data = []
        for result, examination in results:
            mark_rows = self.session.execute(
                select(StudentMark, ExaminationComponent, ExaminationSubject, Subject)
                .join(ExaminationComponent, ExaminationComponent.id == StudentMark.component_id)
                .join(
                    ExaminationSubject,
                    ExaminationSubject.id == ExaminationComponent.examination_subject_id,
                )
                .join(Subject, Subject.id == ExaminationSubject.subject_id)
                .where(
                    StudentMark.student_id == student.id,
                    ExaminationSubject.examination_id == examination.id,
                )
                .order_by(Subject.name, ExaminationComponent.name)
            ).all()
            data.append(
                {
                    "examination_id": examination.id,
                    "examination_name": examination.name,
                    "examination_type": examination.examination_type,
                    "start_date": examination.start_date,
                    "academic_year": self._get_class(examination.class_id).academic_year,
                    "total_max_marks": result.total_max_marks,
                    "total_obtained_marks": result.total_obtained_marks,
                    "percentage": result.percentage,
                    "grade": result.grade,
                    "status": result.result_status,
                    "marks": [
                        {
                            "subject_id": exam_subject.subject_id,
                            "subject_name": subject.name,
                            "component": component.name,
                            "max_marks": component.max_marks,
                            "obtained_marks": mark.obtained_marks,
                            "status": mark.result_status,
                        }
                        for mark, component, exam_subject, subject in mark_rows
                    ],
                }
            )
        return data

    def list_grading_rules(self, scale_code: str) -> list[GradingRule]:
        return list(
            self.session.scalars(
                select(GradingRule)
                .where(GradingRule.scale_code == scale_code)
                .order_by(GradingRule.minimum_percentage)
            ).all()
        )

    def update_grading_rules(
        self,
        scale_code: str,
        payload: GradingScaleUpdateRequest,
        actor_id: int,
        request: Request,
    ) -> list[GradingRule]:
        if not scale_code.strip() or len(scale_code) > 50:
            raise ValidationException("Scale code must be between 1 and 50 characters")
        with transaction(self.session):
            self.session.query(GradingRule).filter(GradingRule.scale_code == scale_code).delete()
            rules = [
                GradingRule(
                    scale_code=scale_code,
                    grade=item.grade,
                    minimum_percentage=item.minimum_percentage,
                    maximum_percentage=item.maximum_percentage,
                    description=item.description,
                )
                for item in payload.rules
            ]
            self.session.add_all(rules)
            self.audit.log(
                action="academics.grading.update",
                entity_type="grading_scale",
                actor_user_id=actor_id,
                new_values={"scale_code": scale_code, "grades": [rule.grade for rule in rules]},
                request=request,
            )
        return self.list_grading_rules(scale_code)

    def _save_marks(self, examination: Examination, rows, actor_id: int) -> None:
        component_ids = {row.component_id for row in rows}
        components = self.session.scalars(
            select(ExaminationComponent)
            .join(ExaminationSubject)
            .where(
                ExaminationSubject.examination_id == examination.id,
                ExaminationComponent.id.in_(component_ids),
            )
        ).all()
        component_by_id = {component.id: component for component in components}
        if len(component_by_id) != len(component_ids):
            raise ValidationException("Every mark must reference a component in this examination")
        student_ids = {row.student_id for row in rows}
        students = self.session.scalars(
            select(Student).where(
                Student.id.in_(student_ids),
                Student.class_id == examination.class_id,
                Student.status == StudentStatus.ACTIVE.value,
                Student.deleted_at.is_(None),
            )
        ).all()
        if len(students) != len(student_ids):
            raise ValidationException(
                "Every student must be active and enrolled in the examination class"
            )
        for row in rows:
            component = component_by_id[row.component_id]
            exam_subject = self.session.get(ExaminationSubject, component.examination_subject_id)
            if not self._student_is_eligible_for_subject(row.student_id, exam_subject):
                raise ValidationException(
                    "Marks can only be entered for a student's enrolled or selected subjects"
                )
            if row.status == "PRESENT" and row.obtained_marks > component.max_marks:
                raise ValidationException(
                    f"Marks cannot exceed {component.max_marks} for component {component.name}"
                )
            mark = self.session.scalar(
                select(StudentMark).where(
                    StudentMark.component_id == row.component_id,
                    StudentMark.student_id == row.student_id,
                )
            )
            if mark is None:
                mark = StudentMark(
                    component_id=row.component_id,
                    student_id=row.student_id,
                    entered_by=actor_id,
                )
                self.session.add(mark)
            mark.obtained_marks = row.obtained_marks
            mark.result_status = (
                "ABSENT"
                if row.status == "ABSENT"
                else "EXEMPTED"
                if row.status == "EXEMPTED"
                else "PASS"
                if row.obtained_marks >= component.passing_marks
                else "FAIL"
            )
            mark.remarks = row.remarks
            mark.updated_by = actor_id

    def _calculate_results(self, examination: Examination) -> None:
        subjects = examination.subjects
        if not subjects:
            raise BusinessRuleException("Examination has no configured subjects")
        subject_ids = {subject.subject_id for subject in subjects}
        mandatory_ids = set(
            self.session.scalars(
                select(ClassSubject.subject_id).where(
                    ClassSubject.class_id == examination.class_id,
                    ClassSubject.subject_type == "mandatory",
                    ClassSubject.is_active.is_(True),
                )
            ).all()
        )
        if not mandatory_ids.issubset(subject_ids):
            raise BusinessRuleException("Every mandatory class subject must be configured")
        students = self.session.scalars(
            select(Student).where(
                Student.class_id == examination.class_id,
                Student.status == StudentStatus.ACTIVE.value,
                Student.deleted_at.is_(None),
            )
        ).all()
        if not students:
            raise BusinessRuleException("There are no active students in the examination class")
        rules = self.list_grading_rules("DEFAULT")
        if not rules:
            raise BusinessRuleException("The default grading scale is not configured")
        result_by_student = {
            result.student_id: result
            for result in self.session.scalars(
                select(ExaminationResult).where(ExaminationResult.examination_id == examination.id)
            ).all()
        }
        for student in students:
            total_max = Decimal("0")
            total_obtained = Decimal("0")
            passed = True
            included_subjects = 0
            for exam_subject in subjects:
                if not self._student_is_eligible_for_subject(student.id, exam_subject):
                    continue
                components = exam_subject.components
                marks = {
                    mark.component_id: mark
                    for mark in self.session.scalars(
                        select(StudentMark)
                        .where(StudentMark.student_id == student.id)
                        .where(StudentMark.component_id.in_([item.id for item in components]))
                    ).all()
                }
                missing = [item.name for item in components if item.id not in marks]
                if missing:
                    raise BusinessRuleException(
                        f"Marks are incomplete for student {student.student_code}: "
                        f"{', '.join(missing)}"
                    )
                included = [
                    component
                    for component in components
                    if marks[component.id].result_status != "EXEMPTED"
                ]
                if not included:
                    continue
                included_subjects += 1
                subject_max = sum((component.max_marks for component in included), Decimal("0"))
                subject_score = Decimal("0")
                subject_passed = True
                for component in included:
                    mark = marks[component.id]
                    score = mark.obtained_marks or Decimal("0")
                    subject_score += score
                    if mark.result_status != "PASS":
                        subject_passed = False
                adjusted_pass_mark = (
                    exam_subject.passing_marks * subject_max / exam_subject.max_marks
                )
                if subject_score < adjusted_pass_mark:
                    subject_passed = False
                total_max += subject_max
                total_obtained += subject_score
                passed = passed and subject_passed
            if included_subjects == 0 or total_max <= 0:
                raise BusinessRuleException(
                    f"Student {student.student_code} has no assessable examination subjects"
                )
            percentage = (total_obtained * Decimal("100") / total_max).quantize(
                CENT, rounding=ROUND_HALF_UP
            )
            grade = next(
                (
                    rule.grade
                    for rule in rules
                    if rule.minimum_percentage <= percentage <= rule.maximum_percentage
                ),
                None,
            )
            if grade is None:
                raise BusinessRuleException("Grading scale does not cover the result percentage")
            result = result_by_student.get(student.id)
            if result is None:
                result = ExaminationResult(
                    examination_id=examination.id,
                    student_id=student.id,
                )
                self.session.add(result)
            result.total_max_marks = total_max
            result.total_obtained_marks = total_obtained
            result.percentage = percentage
            result.grade = grade
            result.result_status = "PASS" if passed else "FAIL"

    def _student_is_eligible_for_subject(
        self,
        student_id: int,
        exam_subject: ExaminationSubject,
    ) -> bool:
        offering = self.session.get(ClassSubject, (exam_subject.class_id, exam_subject.subject_id))
        if offering is None:
            return False
        if offering.subject_type == "mandatory":
            return True
        return (
            self.session.scalar(
                select(StudentSubjectSelection.id).where(
                    StudentSubjectSelection.student_id == student_id,
                    StudentSubjectSelection.class_id == exam_subject.class_id,
                    StudentSubjectSelection.subject_id == exam_subject.subject_id,
                    StudentSubjectSelection.is_active.is_(True),
                )
            )
            is not None
        )

    def _get_class(self, class_id: int) -> Class:
        school_class = self.session.get(Class, class_id)
        if (
            not school_class
            or school_class.status != ClassStatus.ACTIVE.value
            or school_class.deleted_at is not None
        ):
            raise NotFoundException("Active class not found")
        return school_class

    def _get_student(self, student_id: int) -> Student:
        student = self.session.get(Student, student_id)
        if not student or student.deleted_at is not None:
            raise NotFoundException("Student not found")
        return student

    def _student_for_user(self, current_user: User) -> Student:
        student = self.session.scalar(
            select(Student).where(
                Student.user_id == current_user.id,
                Student.deleted_at.is_(None),
            )
        )
        if not student:
            raise NotFoundException("Student portal profile not found")
        return student
