from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.core.responses import success_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.academics import (
    ExaminationCreateRequest,
    GradingScaleUpdateRequest,
    MarksBatchRequest,
    MarksCorrectionRequest,
    SubjectOfferingRequest,
)
from app.services.academics import AcademicService

router = APIRouter(prefix="/academics", tags=["academics"])


def _examination_data(examination) -> dict:
    return {
        "id": examination.id,
        "name": examination.name,
        "class_id": examination.class_id,
        "examination_type": examination.examination_type,
        "start_date": examination.start_date,
        "end_date": examination.end_date,
        "status": examination.status,
        "description": examination.description,
        "subjects": [
            {
                "id": subject.id,
                "subject_id": subject.subject_id,
                "teacher_id": subject.teacher_id,
                "max_marks": subject.max_marks,
                "passing_marks": subject.passing_marks,
                "components": [
                    {
                        "id": component.id,
                        "name": component.name,
                        "type": component.component_type,
                        "max_marks": component.max_marks,
                        "passing_marks": component.passing_marks,
                    }
                    for component in subject.components
                ],
            }
            for subject in examination.subjects
        ],
    }


@router.get("/classes/{class_id}/subjects")
def list_class_subjects(
    class_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("academics.subjects.manage"))],
):
    data = AcademicService(db).list_offerings(class_id)
    return success_response("Class subject offerings fetched successfully", data, request)


@router.put("/classes/{class_id}/subjects/{subject_id}")
def configure_class_subject(
    class_id: int,
    subject_id: int,
    payload: SubjectOfferingRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("academics.subjects.manage"))],
):
    data = AcademicService(db).configure_offering(
        class_id,
        subject_id,
        payload,
        user.id,
        request,
    )
    return success_response("Class subject offering saved successfully", data, request)


@router.put("/classes/{class_id}/subjects/{subject_id}/teacher")
def assign_class_subject_teacher(
    class_id: int,
    subject_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("academics.subjects.manage"))],
    teacher_id: int = Query(gt=0),
):
    data = AcademicService(db).assign_teacher(
        class_id,
        subject_id,
        teacher_id,
        user.id,
        request,
    )
    return success_response("Class subject teacher assigned successfully", data, request)


@router.get("/students/me/subjects")
def list_my_subjects(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("academics.results.read"))],
):
    data = AcademicService(db).student_subjects(user)
    return success_response("Your subjects fetched successfully", data, request)


@router.get("/students/me/results")
def list_my_results(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("academics.results.read"))],
):
    data = AcademicService(db).student_results(user)
    return success_response("Your published results fetched successfully", data, request)


@router.get("/students/{student_id}/subjects")
def list_student_subjects(
    student_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("academics.electives.manage"))],
):
    data = AcademicService(db).list_subject_selections(student_id)
    return success_response("Student subjects fetched successfully", data, request)


@router.put("/students/{student_id}/electives")
def update_student_electives(
    student_id: int,
    subject_ids: list[int],
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("academics.electives.manage"))],
):
    data = AcademicService(db).set_student_electives(
        student_id,
        subject_ids,
        user.id,
        request,
    )
    return success_response("Student elective selections updated successfully", data, request)


@router.post("/examinations", status_code=status.HTTP_201_CREATED)
def create_examination(
    payload: ExaminationCreateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("academics.examinations.manage"))],
):
    examination = AcademicService(db).create_examination(payload, user.id, request)
    return success_response(
        "Examination created as draft",
        _examination_data(examination),
        request,
    )


@router.get("/examinations")
def list_examinations(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("academics.examinations.manage"))],
    class_id: int | None = Query(default=None, gt=0),
):
    examinations = AcademicService(db).list_examinations(class_id)
    return success_response(
        "Examinations fetched successfully",
        [_examination_data(examination) for examination in examinations],
        request,
    )


@router.get("/examinations/{examination_id}")
def get_examination(
    examination_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("academics.examinations.manage"))],
):
    examination = AcademicService(db).get_examination(examination_id)
    return success_response(
        "Examination fetched successfully", _examination_data(examination), request
    )


@router.post("/examinations/{examination_id}/schedule")
def schedule_examination(
    examination_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("academics.examinations.manage"))],
):
    examination = AcademicService(db).schedule_examination(
        examination_id,
        user.id,
        request,
    )
    return success_response(
        "Examination scheduled successfully",
        _examination_data(examination),
        request,
    )


@router.post("/examinations/{examination_id}/marks")
def enter_marks(
    examination_id: int,
    payload: MarksBatchRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("academics.marks.manage"))],
):
    data = AcademicService(db).enter_marks(
        examination_id,
        payload,
        user.id,
        request,
    )
    return success_response("Examination marks saved successfully", data, request)


@router.get("/examinations/{examination_id}/roster")
def get_examination_roster(
    examination_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("academics.marks.manage"))],
):
    data = AcademicService(db).examination_roster(examination_id)
    return success_response("Examination roster fetched successfully", data, request)


@router.post("/examinations/{examination_id}/publish")
def publish_examination(
    examination_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("academics.examinations.manage"))],
):
    examination = AcademicService(db).publish_examination(
        examination_id,
        user.id,
        request,
    )
    return success_response(
        "Examination results published successfully",
        _examination_data(examination),
        request,
    )


@router.post("/examinations/{examination_id}/lock")
def lock_examination(
    examination_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("academics.examinations.manage"))],
):
    examination = AcademicService(db).lock_examination(
        examination_id,
        user.id,
        request,
    )
    return success_response(
        "Examination results locked successfully",
        _examination_data(examination),
        request,
    )


@router.post("/examinations/{examination_id}/corrections")
def correct_marks(
    examination_id: int,
    payload: MarksCorrectionRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("academics.marks.correct"))],
):
    data = AcademicService(db).correct_marks(
        examination_id,
        payload,
        user.id,
        request,
    )
    return success_response("Published marks corrected and results recalculated", data, request)


@router.get("/examinations/{examination_id}/results")
def list_examination_results(
    examination_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("academics.examinations.manage"))],
):
    data = AcademicService(db).list_results(examination_id)
    return success_response("Published examination results fetched successfully", data, request)


@router.get("/grading-scales/{scale_code}")
def list_grading_rules(
    scale_code: str,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[User, Depends(require_permissions("academics.examinations.manage"))],
):
    rules = AcademicService(db).list_grading_rules(scale_code)
    data = [
        {
            "grade": rule.grade,
            "minimum_percentage": rule.minimum_percentage,
            "maximum_percentage": rule.maximum_percentage,
            "description": rule.description,
        }
        for rule in rules
    ]
    return success_response("Grading scale fetched successfully", data, request)


@router.put("/grading-scales/{scale_code}")
def update_grading_rules(
    scale_code: str,
    payload: GradingScaleUpdateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("academics.grading.manage"))],
):
    rules = AcademicService(db).update_grading_rules(
        scale_code,
        payload,
        user.id,
        request,
    )
    data = [
        {
            "grade": rule.grade,
            "minimum_percentage": rule.minimum_percentage,
            "maximum_percentage": rule.maximum_percentage,
            "description": rule.description,
        }
        for rule in rules
    ]
    return success_response("Grading scale updated successfully", data, request)
