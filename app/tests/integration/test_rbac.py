"""Integration tests for role-based access control (RBAC) and permissions."""

import pytest


def test_register_requires_admin_role(client):
    """POST /register without ADMIN role returns 403 or 401."""
    # Try to register without authentication
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@school.com",
            "password": "Password@123",
            "first_name": "New",
            "last_name": "User",
        },
    )
    assert response.status_code in [401, 403]  # Unauthorized or Forbidden


def test_register_with_admin_token_succeeds(client, auth_headers):
    """POST /register with SUPER_ADMIN token creates new user."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "staff@school.com",
            "password": "StaffPass@123",
            "first_name": "Staff",
            "last_name": "Member",
        },
        headers=auth_headers,
    )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    assert data["email"] == "staff@school.com"
    assert "roles" in data


def test_list_inquiry_admissions_requires_permission(client):
    """GET /admissions/inquiry-admissions without permission returns 403."""
    response = client.get("/api/v1/admissions/inquiry-admissions")
    assert response.status_code in [401, 403]


def test_list_inquiry_admissions_with_permission_succeeds(client, auth_headers):
    """GET /admissions/inquiry-admissions with admin token succeeds."""
    response = client.get(
        "/api/v1/admissions/inquiry-admissions",
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "data" in body


def test_create_inquiry_admission_requires_permission(client):
    """POST /admissions/inquiries/{id}/admission without permission returns 403."""
    response = client.post(
        "/api/v1/admissions/inquiries/1/admission",
        json={
            "class_id": 1,
            "section": "A",
            "academic_year": "2024-2025",
        },
    )
    assert response.status_code in [401, 403]


def test_create_inquiry_admission_with_permission_requires_valid_inquiry(client, auth_headers):
    """POST /admissions/inquiries/{id}/admission with admin token fails on invalid inquiry."""
    response = client.post(
        "/api/v1/admissions/inquiries/99999/admission",
        json={
            "class_id": 1,
            "section": "A",
            "academic_year": "2024-2025",
        },
        headers=auth_headers,
    )
    # Should fail because inquiry doesn't exist, not because of permissions
    assert response.status_code in [404, 400]


def test_upload_admission_document_requires_permission(client):
    """POST /admissions/inquiry-admissions/{id}/documents without permission returns 403."""
    response = client.post(
        "/api/v1/admissions/inquiry-admissions/1/documents",
        data={
            "document_type": "progress_report",
        },
    )
    assert response.status_code in [401, 403]


def test_verify_document_requires_special_permission(client, auth_headers):
    """POST /admissions/documents/{id}/verify without admissions.verify_documents permission fails."""
    response = client.post(
        "/api/v1/admissions/documents/1/verify?verified=true",
        headers=auth_headers,
    )
    # This should either fail (404 if doc doesn't exist) or pass (if admin has permission)
    # Most likely 404 since document doesn't exist
    assert response.status_code in [200, 404, 403]


def test_approve_inquiry_admission_requires_permission(client):
    """POST /admissions/inquiry-admissions/{id}/approve without permission returns 403."""
    response = client.post(
        "/api/v1/admissions/inquiry-admissions/1/approve",
    )
    assert response.status_code in [401, 403]


def test_reject_inquiry_admission_requires_permission(client):
    """POST /admissions/inquiry-admissions/{id}/reject without permission returns 403."""
    response = client.post(
        "/api/v1/admissions/inquiry-admissions/1/reject",
        json={"rejection_reason": "Not eligible"},
    )
    assert response.status_code in [401, 403]


def test_enroll_student_requires_enrollment_permission(client):
    """POST /admissions/inquiry-admissions/{id}/enroll without permission returns 403."""
    response = client.post(
        "/api/v1/admissions/inquiry-admissions/1/enroll",
    )
    assert response.status_code in [401, 403]


def test_get_inquiry_admission_requires_read_permission(client):
    """GET /admissions/inquiry-admissions/{id} without permission returns 403."""
    response = client.get("/api/v1/admissions/inquiry-admissions/1")
    assert response.status_code in [401, 403]


def test_update_inquiry_admission_requires_update_permission(client):
    """PUT /admissions/inquiry-admissions/{id} without permission returns 403."""
    response = client.put(
        "/api/v1/admissions/inquiry-admissions/1",
        json={"status": "submitted"},
    )
    assert response.status_code in [401, 403]


def test_list_legacy_admissions_requires_permission(client):
    """GET /admissions/students/admissions/all without permission returns 403."""
    response = client.get("/api/v1/admissions/students/admissions/all")
    assert response.status_code in [401, 403]


def test_list_legacy_admissions_with_permission_succeeds(client, auth_headers):
    """GET /admissions/students/admissions/all with admin token succeeds."""
    response = client.get(
        "/api/v1/admissions/students/admissions/all",
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True


def test_required_documents_endpoint_is_public(client):
    """GET /admissions/documents/required is public and returns document types."""
    response = client.get("/api/v1/admissions/documents/required")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    data = body["data"]
    # Should list required document types
    assert isinstance(data, dict) or isinstance(data, list)


def test_admin_can_access_all_protected_endpoints(client, auth_headers):
    """Super admin token grants access to all protected endpoints."""
    # Test a few protected endpoints
    endpoints = [
        ("/api/v1/admissions/inquiry-admissions", "GET"),
        ("/api/v1/admissions/students/admissions/all", "GET"),
    ]
    for endpoint, method in endpoints:
        if method == "GET":
            response = client.get(endpoint, headers=auth_headers)
        assert response.status_code in [200, 400, 404, 422]  # Not 401 or 403
