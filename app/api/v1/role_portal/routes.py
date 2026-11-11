from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, Request, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import require_permissions
from app.core.responses import success_response
from app.db.session import get_db
from app.models.user import User
from app.schemas.role_portal import (
    AssessmentCreateRequest,
    AssessmentResponse,
    AssessmentResultRequest,
    AssessmentResultResponse,
    AssessmentResultResponse,
    AssessmentUpdateRequest,
    AssignmentCreateRequest,
    AssignmentResponse,
    AssignmentUpdateRequest,
    EventCreateRequest,
    EventResponse,
    EventReviewRequest,
    EventUpdateRequest,
    TimetableCreateRequest,
    TimetableResponse,
    TimetableUpdateRequest,
)
from app.services.role_portal import RolePortalService

router = APIRouter()


def _assessment_response(assessment, user: User, service: RolePortalService):
    response = AssessmentResponse.model_validate(assessment).model_dump()
    response["results"] = [
        AssessmentResultResponse.model_validate(result).model_dump()
        for result in service.visible_assessment_results(assessment, user)
    ]
    return response


@router.get("/teachers/me/class-subjects")
def list_my_teaching_assignments(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("teaching_assignments.manage"))],
):
    assignments = RolePortalService(db).list_own_teaching_assignments(user)
    data = [
        {
            "class_id": class_id,
            "subject_id": subject_id,
            "class_name": class_name,
            "subject_name": subject_name,
        }
        for class_id, subject_id, class_name, subject_name in assignments
    ]
    return success_response("Teaching assignments fetched successfully", data, request)


@router.post("/teachers/me/class-subjects", status_code=status.HTTP_201_CREATED)
def add_my_teaching_assignment(
    class_id: int,
    subject_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("teaching_assignments.manage"))],
):
    RolePortalService(db).add_own_teaching_assignment(user, class_id, subject_id, request)
    return success_response(
        "Teacher mapped to class subject successfully",
        {"class_id": class_id, "subject_id": subject_id},
        request,
    )


@router.delete("/teachers/me/class-subjects/{class_id}/{subject_id}")
def remove_my_teaching_assignment(
    class_id: int,
    subject_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("teaching_assignments.manage"))],
):
    RolePortalService(db).remove_own_teaching_assignment(
        user,
        class_id,
        subject_id,
        request,
    )
    return success_response("Teaching assignment removed successfully", None, request)


@router.get("/assignments")
def list_assignments(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("assignments.read"))],
    class_id: int | None = Query(default=None, gt=0),
):
    assignments = RolePortalService(db).list_assignments(user, class_id)
    data = [AssignmentResponse.model_validate(item).model_dump() for item in assignments]
    return success_response("Assignments fetched successfully", data, request)


@router.post("/assignments", status_code=status.HTTP_201_CREATED)
def create_assignment(
    payload: AssignmentCreateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("assignments.create"))],
):
    assignment = RolePortalService(db).create_assignment(payload, user, request)
    return success_response(
        "Assignment created as draft",
        AssignmentResponse.model_validate(assignment).model_dump(),
        request,
    )


@router.get("/assignments/{assignment_id}")
def get_assignment(
    assignment_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("assignments.read"))],
):
    assignment = RolePortalService(db).get_assignment(assignment_id, user)
    return success_response(
        "Assignment fetched successfully",
        AssignmentResponse.model_validate(assignment).model_dump(),
        request,
    )


@router.put("/assignments/{assignment_id}")
def update_assignment(
    assignment_id: int,
    payload: AssignmentUpdateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("assignments.update"))],
):
    assignment = RolePortalService(db).update_assignment(
        assignment_id,
        payload,
        user,
        request,
    )
    return success_response(
        "Assignment updated successfully",
        AssignmentResponse.model_validate(assignment).model_dump(),
        request,
    )


@router.post("/assignments/{assignment_id}/publish")
def publish_assignment(
    assignment_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("assignments.publish"))],
):
    assignment = RolePortalService(db).change_assignment_status(
        assignment_id,
        "published",
        user,
        request,
    )
    return success_response(
        "Assignment published successfully",
        AssignmentResponse.model_validate(assignment).model_dump(),
        request,
    )


@router.post("/assignments/{assignment_id}/close")
def close_assignment(
    assignment_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("assignments.update"))],
):
    assignment = RolePortalService(db).change_assignment_status(
        assignment_id,
        "closed",
        user,
        request,
    )
    return success_response(
        "Assignment closed successfully",
        AssignmentResponse.model_validate(assignment).model_dump(),
        request,
    )


@router.post("/assignments/{assignment_id}/attachments", status_code=status.HTTP_201_CREATED)
def upload_assignment_attachment(
    assignment_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("assignments.update"))],
    file: Annotated[UploadFile, File(description="PDF, JPG, JPEG, or PNG attachment.")],
):
    attachment = RolePortalService(db).upload_assignment_attachment(
        assignment_id,
        file,
        user,
        request,
    )
    return success_response(
        "Assignment attachment uploaded successfully",
        {
            "id": attachment.id,
            "file_name": attachment.file_name,
            "content_type": attachment.content_type,
            "created_at": attachment.created_at,
        },
        request,
    )


@router.get("/assignments/{assignment_id}/attachments/{attachment_id}")
def download_assignment_attachment(
    assignment_id: int,
    attachment_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("assignments.read"))],
):
    attachment, path = RolePortalService(db).get_assignment_attachment(
        assignment_id,
        attachment_id,
        user,
    )
    return FileResponse(
        path=Path(path),
        filename=attachment.file_name,
        media_type="application/octet-stream",
    )


@router.get("/timetable")
def list_timetable(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("timetable.read"))],
    class_id: int | None = Query(default=None, gt=0),
    academic_year: str | None = Query(default=None, min_length=1, max_length=20),
):
    entries = RolePortalService(db).list_timetable(user, class_id, academic_year)
    data = [TimetableResponse.model_validate(item).model_dump() for item in entries]
    return success_response("Timetable fetched successfully", data, request)


@router.post("/timetable", status_code=status.HTTP_201_CREATED)
def create_timetable_entry(
    payload: TimetableCreateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("timetable.create"))],
):
    entry = RolePortalService(db).create_timetable_entry(payload, user, request)
    return success_response(
        "Timetable entry created successfully",
        TimetableResponse.model_validate(entry).model_dump(),
        request,
    )


@router.put("/timetable/{entry_id}")
def update_timetable_entry(
    entry_id: int,
    payload: TimetableUpdateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("timetable.update"))],
):
    entry = RolePortalService(db).update_timetable_entry(entry_id, payload, user, request)
    return success_response(
        "Timetable entry updated successfully",
        TimetableResponse.model_validate(entry).model_dump(),
        request,
    )


@router.get("/assessments")
def list_assessments(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("assessments.read"))],
    class_id: int | None = Query(default=None, gt=0),
):
    service = RolePortalService(db)
    assessments = service.list_assessments(user, class_id)
    data = [_assessment_response(item, user, service) for item in assessments]
    return success_response("Assessments fetched successfully", data, request)


@router.post("/assessments", status_code=status.HTTP_201_CREATED)
def create_assessment(
    payload: AssessmentCreateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("assessments.create"))],
):
    service = RolePortalService(db)
    assessment = service.create_assessment(payload, user, request)
    return success_response(
        "Assessment created as unpublished",
        _assessment_response(assessment, user, service),
        request,
    )


@router.get("/assessments/{assessment_id}")
def get_assessment(
    assessment_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("assessments.read"))],
):
    service = RolePortalService(db)
    assessment = service.get_assessment(assessment_id, user)
    return success_response(
        "Assessment fetched successfully",
        _assessment_response(assessment, user, service),
        request,
    )


@router.put("/assessments/{assessment_id}")
def update_assessment(
    assessment_id: int,
    payload: AssessmentUpdateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("assessments.update"))],
):
    assessment = RolePortalService(db).update_assessment(
        assessment_id,
        payload,
        user,
        request,
    )
    return success_response(
        "Assessment updated successfully",
        AssessmentResponse.model_validate(assessment).model_dump(),
        request,
    )


@router.put("/assessments/{assessment_id}/results/{student_id}")
def upsert_assessment_result(
    assessment_id: int,
    student_id: int,
    payload: AssessmentResultRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("assessments.update"))],
):
    result = RolePortalService(db).upsert_assessment_result(
        assessment_id,
        student_id,
        payload,
        user,
        request,
    )
    return success_response(
        "Assessment result saved successfully",
        AssessmentResultResponse.model_validate(result).model_dump(),
        request,
    )


@router.post("/assessments/{assessment_id}/publish")
def publish_assessment(
    assessment_id: int,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("assessments.publish"))],
):
    service = RolePortalService(db)
    assessment = service.publish_assessment(assessment_id, user, request)
    return success_response(
        "Assessment published successfully",
        _assessment_response(assessment, user, service),
        request,
    )


@router.get("/events")
def list_events(
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("events.read"))],
):
    events = RolePortalService(db).list_events(user)
    data = [EventResponse.model_validate(item).model_dump() for item in events]
    return success_response("Events fetched successfully", data, request)


@router.post("/events", status_code=status.HTTP_201_CREATED)
def create_event(
    payload: EventCreateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("events.create"))],
):
    event = RolePortalService(db).create_event(payload, user, request)
    message = (
        "Event published successfully"
        if event.status == "published"
        else "Event submitted for administrator review"
    )
    return success_response(message, EventResponse.model_validate(event).model_dump(), request)


@router.put("/events/{event_id}")
def update_event(
    event_id: int,
    payload: EventUpdateRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("events.update"))],
):
    event = RolePortalService(db).update_event(event_id, payload, user, request)
    return success_response(
        "Event updated successfully",
        EventResponse.model_validate(event).model_dump(),
        request,
    )


@router.post("/events/{event_id}/review")
def review_event(
    event_id: int,
    payload: EventReviewRequest,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(require_permissions("events.review"))],
):
    event = RolePortalService(db).review_event(event_id, payload, user, request)
    return success_response(
        f"Event {event.status}",
        EventResponse.model_validate(event).model_dump(),
        request,
    )
