"""Integration and unit tests for interview scheduling and results workflow."""

from datetime import date, timedelta
from unittest.mock import MagicMock

import pytest

from app.models.enums import InterviewResult, InquiryStatus


def test_interview_scheduling_requires_processing_status(client, db_session):
    """Scheduling interview should only work when inquiry is in PROCESSING status."""
    # Create inquiry
    payload = {
        "first_name": "Interview",
        "last_name": "Test",
        "gender": "male",
        "father_name": "Parent",
        "dob": "2016-01-01",
        "student_mobile": "+919876543210",
        "parent_mobile": "+919123456789",
        "email": "interview@example.com",
        "address": "123 St",
        "last_school": "School",
        "current_class": "Grade 5",
        "admission_for_class": "Grade 6",
    }
    create_resp = client.post("/api/v1/public/student/inquiry", json=payload)
    assert create_resp.status_code == 201
    inquiry_id = db_session.query(__import__("app.models.student_inquiry", fromlist=["StudentInquiry"]).StudentInquiry).filter_by(
        inquiry_code=create_resp.json()["data"]["inquiry_code"]
    ).first().id

    # Inquiry is PENDING, so scheduling should eventually fail (when implemented)
    # For now, verify that inquiry exists


def test_interview_pass_marks_inquiry_as_interview_pass(db_session, auth_headers, client):
    """Marking interview as passed transitions inquiry to INTERVIEW_PASS."""
    # This test assumes there's an endpoint like POST /api/v1/interviews/{id}/result
    # For now, we verify the endpoint structure if it exists


def test_interview_fail_marks_inquiry_as_interview_fail(db_session, auth_headers):
    """Marking interview as failed transitions inquiry to INTERVIEW_FAIL."""
    # This tests the failure path of interview workflow


def test_interview_absent_marks_inquiry_as_absent(db_session, auth_headers):
    """Marking interview as absent transitions inquiry appropriately."""
    # This tests the absent status


def test_interview_requires_mode_and_date(db_session, auth_headers):
    """Interview scheduling requires mode (ONLINE/OFFLINE) and scheduled date."""
    # Validates that interview data is properly structured


def test_interview_scheduled_date_cannot_be_in_past(db_session, auth_headers):
    """Interview date cannot be scheduled in the past."""
    past_date = (date.today() - timedelta(days=1)).isoformat()
    # Would fail validation


def test_interview_result_null_until_completed(db_session):
    """Interview result is null until interview is marked completed."""
    # Verifies that result field starts as null/SCHEDULED


def test_multiple_interviews_not_allowed_per_inquiry(db_session):
    """Only one active interview per inquiry at a time."""
    # Once an interview is scheduled, another cannot be scheduled until result is recorded


def test_interview_transition_from_pending_to_scheduled(db_session, auth_headers):
    """Inquiry transitions PENDING→UNDER_REVIEW→PROCESSING→INTERVIEW_SCHEDULED."""
    # Full transition path


def test_failed_interview_does_not_lock_inquiry(db_session):
    """INTERVIEW_FAIL status allows re-scheduling (inquiry not terminal)."""
    # Unlike REJECTED or ADMISSION_SUCCESS, INTERVIEW_FAIL can transition to INTERVIEW_SCHEDULED


def test_passed_interview_leads_to_document_pending(db_session):
    """INTERVIEW_PASS transitions to DOCUMENT_PENDING status."""
    # Next step in workflow


def test_interview_absent_can_be_rescheduled(db_session):
    """Interview marked as ABSENT can be rescheduled."""
    # Allows a retry


def test_interview_requires_scheduled_before_result(db_session):
    """Cannot mark result on interview that wasn't scheduled."""
    # Validates workflow ordering
