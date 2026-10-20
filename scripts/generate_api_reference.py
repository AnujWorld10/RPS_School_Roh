"""Generate the Markdown API reference from the application's OpenAPI contract."""

from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path
from typing import Any

from app.main import app
from app.schemas import (
    admissions,
    auth,
    classes,
    enrollment,
    inquiries,
    interviews,
    students,
    subjects,
    teachers,
)

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "api-reference.md"
HTTP_METHODS = {"delete", "get", "patch", "post", "put"}

RESPONSE_MODELS = {
    "approve_inquiry_admission": ("InquiryAdmissionResponse", False),
    "assign_student_class": ("StudentResponse", False),
    "create_class": ("ClassResponse", False),
    "create_inquiry_admission": ("InquiryAdmissionResponse", False),
    "create_salary_payment": ("SalaryPaymentResponse", False),
    "create_student": ("StudentResponse", False),
    "create_teacher": ("TeacherResponse", False),
    "enroll_student": ("EnrollmentResponse", False),
    "get_class": ("ClassResponse", False),
    "get_inquiry": ("StudentInquiryResponse", False),
    "get_inquiry_admission": ("InquiryAdmissionResponse", False),
    "get_interview": ("InterviewResponse", False),
    "get_me": ("UserResponse", False),
    "get_inquiry_status": ("PublicInquiryStatusResponse", False),
    "get_student": ("StudentResponse", False),
    "get_teacher": ("TeacherResponse", False),
    "get_teacher_salary": ("SalaryResponse", False),
    "list_classes": ("ClassResponse", True),
    "list_inquiries": ("StudentInquiryResponse", True),
    "list_inquiry_admissions": ("InquiryAdmissionResponse", True),
    "list_inquiry_interviews": ("InterviewResponse", False),
    "list_legacy_admissions": ("AdmissionResponse", True),
    "list_students": ("StudentResponse", True),
    "list_teachers": ("TeacherResponse", True),
    "login_user": ("TokenResponse", False),
    "record_attendance": ("AttendanceResponse", False),
    "record_interview_result": ("InterviewResponse", False),
    "refresh_token": ("RefreshTokenResponse", False),
    "register_user": ("RegisterUserResponse", False),
    "reject_inquiry_admission": ("InquiryAdmissionResponse", False),
    "reject_inquiry": ("StudentInquiryResponse", False),
    "schedule_interview": ("InterviewResponse", False),
    "start_inquiry_review": ("StudentInquiryResponse", False),
    "mark_inquiry_processing": ("StudentInquiryResponse", False),
    "update_class": ("ClassResponse", False),
    "update_inquiry_admin": ("StudentInquiryResponse", False),
    "update_inquiry_admission": ("InquiryAdmissionResponse", False),
    "update_student": ("StudentResponse", False),
    "update_student_status": ("StudentResponse", False),
    "update_student_inquiry": ("PublicInquiryStatusResponse", False),
    "update_teacher": ("TeacherResponse", False),
    "upload_admission_document": ("AdmissionDocumentResponse", False),
    "verify_document": ("AdmissionDocumentResponse", False),
    "verify_token": ("VerifyTokenResponse", False),
}

RESPONSE_MODULES = (
    admissions,
    auth,
    classes,
    enrollment,
    inquiries,
    interviews,
    students,
    subjects,
    teachers,
)
MODEL_REGISTRY = {
    model.__name__: model
    for module in RESPONSE_MODULES
    for model in vars(module).values()
    if isinstance(model, type) and hasattr(model, "model_json_schema")
}

CUSTOM_RESPONSE_DATA = {
    "activate_subject": (
        {"id": 1, "code": "MATH", "name": "Mathematics", "is_active": True},
        False,
    ),
    "assign_class": ({"class_id": 1}, False),
    "assign_subject": ({"subject_id": 1}, False),
    "assign_class_subject": ({"class_id": 1, "subject_id": 1}, False),
    "assign_class_teacher": ({"class_id": 1, "teacher_id": 1}, False),
    "assign_teacher_class_subject": (
        {"teacher_id": 1, "class_id": 1, "subject_id": 1},
        False,
    ),
    "change_password": (None, False),
    "delete_class": (None, False),
    "delete_student": (None, False),
    "deactivate_subject": (
        {"id": 1, "code": "MATH", "name": "Mathematics", "is_active": False},
        False,
    ),
    "get_class_academic_readiness": (
        {
            "class_id": 1,
            "ready": True,
            "class_teacher_id": 1,
            "active_subject_ids": [1],
            "issues": [],
        },
        False,
    ),
    "get_subject": (
        {"id": 1, "code": "MATH", "name": "Mathematics", "is_active": True},
        False,
    ),
    "get_teacher_academic_readiness": (
        {
            "teacher_id": 1,
            "ready": True,
            "assignments": [
                {
                    "class_id": 1,
                    "subject_id": 1,
                    "class_name": "Grade 5",
                    "subject_name": "Mathematics",
                }
            ],
            "issues": [],
        },
        False,
    ),
    "list_class_subjects": (
        [{"id": 1, "code": "MATH", "name": "Mathematics", "is_active": True}],
        False,
    ),
    "list_student_subjects": (
        [{"id": 1, "code": "MATH", "name": "Mathematics", "is_active": True}],
        False,
    ),
    "list_subjects": (
        [{"id": 1, "code": "MATH", "name": "Mathematics", "is_active": True}],
        True,
    ),
    "list_teacher_class_subjects": (
        [
            {
                "class_id": 1,
                "subject_id": 1,
                "class_name": "Grade 5",
                "subject_name": "Mathematics",
            }
        ],
        False,
    ),
    "list_required_documents": (
        {
            "required": [
                "progress_report",
                "transfer_certificate",
                "migration_certificate",
                "character_certificate",
                "student_aadhar",
                "parent_aadhar",
            ]
        },
        False,
    ),
    "list_teacher_classes": (
        [{"id": 1, "name": "Grade 5", "section": "A", "academic_year": "2026-2027"}],
        False,
    ),
    "list_teacher_subjects": (
        [{"id": 1, "code": "MATH", "name": "Mathematics"}],
        False,
    ),
    "logout_user": (None, False),
    "remove_class_subject": (None, False),
    "remove_class_teacher": (None, False),
    "remove_teacher_class_subject": (None, False),
    "replace_class_teacher": ({"class_id": 1, "teacher_id": 1}, False),
    "create_subject": (
        {"id": 1, "code": "MATH", "name": "Mathematics", "is_active": True},
        False,
    ),
    "update_subject": (
        {"id": 1, "code": "MATH", "name": "Mathematics", "is_active": True},
        False,
    ),
    "submit_student_inquiry": (
        {"inquiry_code": "INQ202600007", "status": "PENDING"},
        False,
    ),
    "submit_admission": (
        {"admission_code": "ADM202600001", "status": "submitted"},
        False,
    ),
    "liveness_check": ({"status": "alive"}, False),
    "readiness_check": ({"status": "ready", "database": True}, False),
}

SAMPLE_VALUES = {
    "academic_year": "2026-2027",
    "access_token": "example-access-token-not-valid",
    "address": "12 School Road, Pune",
    "admission_code": "ADM202600001",
    "admission_for_class": "Grade 5",
    "admission_for_class_id": 1,
    "attendance_date": "2026-10-19",
    "base_salary": 50000.00,
    "blood_group": "O+",
    "class_id": 1,
    "current_class": "Grade 4",
    "current_password": "ExampleCurrentPassword!2026",
    "date_of_birth": "2018-04-12",
    "dob": "2018-04-12",
    "email": "parent@example.com",
    "employee_no": "EMP-2026-001",
    "father_name": "Rohit Sharma",
    "file_name": "progress-report.pdf",
    "first_name": "Aarav",
    "deduction_amount": 2500.00,
    "change_reason": "Inquiry moved to staff review.",
    "gender": "male",
    "gross_amount": 50000.00,
    "internal_notes": "Documents reviewed by the admissions office.",
    "inquiry_code": "INQ202600007",
    "from_status": "PENDING",
    "last_name": "Sharma",
    "last_school": "Green Valley School",
    "last_school_percentage": 87.50,
    "location": "Room 101",
    "mode": "OFFLINE",
    "middle_name": None,
    "name": "Grade 5",
    "nationality": "Indian",
    "net_amount": 47500.00,
    "parent_mobile": "+919876543210",
    "payment_month": "2026-10",
    "password": "ExamplePassword!2026",
    "phone": "+919876543211",
    "permanent_address": "12 School Road, Pune",
    "reason": "Updated student enrollment status.",
    "reason_for_school_change": "Family relocation.",
    "rejection_reason": "Required admission document is missing.",
    "remarks": "Please bring the previous report card.",
    "result": "SCHEDULED",
    "schedule_date": "2026-11-05",
    "schedule_time": "10:30:00",
    "section": "A",
    "status": "active",
    "student_id": 1,
    "student_code": "STU202600001",
    "student_mobile": None,
    "subject_id": 1,
    "temporary_address": "12 School Road, Pune",
    "teacher_id": 1,
    "to_status": "UNDER_REVIEW",
    "notes": "Applicant will provide the original documents at the office.",
    "refresh_token": "example-refresh-token-not-valid",
    "user_id": 1,
    "new_password": "ExampleNewPassword!2026",
}

MODEL_FIELD_EXAMPLES = {
    "AdmissionDocumentResponse": {
        "document_type": "progress_report",
        "file_path": "uploads/admissions/1/progress-report.pdf",
        "verification_status": "PENDING",
    },
    "AdmissionResponse": {"status": "submitted"},
    "AttendanceResponse": {"status": "present"},
    "ClassResponse": {"status": "active"},
    "InquiryAdmissionResponse": {"status": "submitted", "documents": []},
    "InterviewResponse": {"mode": "OFFLINE", "result": "SCHEDULED"},
    "PublicInquiryStatusResponse": {"status": "PENDING"},
    "RegisterUserResponse": {"roles": ["TEACHER"], "status": "active"},
    "SalaryPaymentResponse": {"status": "paid"},
    "SalaryResponse": {"status": "active"},
    "StudentInquiryResponse": {
        "gender": "male",
        "status": "PENDING",
        "status_timeline": [],
    },
    "StudentResponse": {"gender": "male", "status": "active"},
    "TeacherResponse": {"status": "active"},
    "UserResponse": {
        "permissions": ["teachers.read"],
        "roles": ["TEACHER"],
        "status": "active",
    },
}

HANDLER_FIELD_EXAMPLES = {
    "start_inquiry_review": {"status": "UNDER_REVIEW"},
}


def markdown_text(value: Any) -> str:
    """Escape text for safe use in a Markdown table cell."""
    return str(value).replace("|", r"\|").replace("\r\n", " ").replace("\n", " ")


def schema_type(schema: dict[str, Any]) -> str:
    if "$ref" in schema:
        name = schema["$ref"].rsplit("/", 1)[-1]
        return f"[`{name}`](#{name.lower()})"

    if "allOf" in schema or "anyOf" in schema or "oneOf" in schema:
        key = next(name for name in ("allOf", "anyOf", "oneOf") if name in schema)
        return f"{key}: " + ", ".join(schema_type(item) for item in schema[key])

    value = schema.get("type", "object")
    if value == "array":
        value = f"array of {schema_type(schema.get('items', {}))}"
    if schema.get("format"):
        value += f" ({schema['format']})"
    if schema.get("nullable"):
        value += ", nullable"
    return value


def schema_constraints(schema: dict[str, Any]) -> str:
    constraints = []
    for key, label in (
        ("enum", "Allowed values"),
        ("minLength", "Min length"),
        ("maxLength", "Max length"),
        ("minimum", "Minimum"),
        ("maximum", "Maximum"),
        ("minItems", "Min items"),
        ("maxItems", "Max items"),
        ("pattern", "Pattern"),
        ("default", "Default"),
    ):
        if key in schema:
            value = ", ".join(map(str, schema[key])) if key == "enum" else schema[key]
            constraints.append(f"{label}: `{markdown_text(value)}`")
    return "; ".join(constraints) or "—"


def first_example(value: Any) -> Any:
    if isinstance(value, list):
        return value[0] if value else None
    if isinstance(value, dict):
        first = next(iter(value.values()), None)
        return first.get("value") if isinstance(first, dict) else first
    return value


def operation_schema(schema: dict[str, Any], include_description: bool = True) -> str:
    if not schema:
        return "—"
    description = schema.get("description")
    details = [schema_type(schema)]
    if schema.get("enum"):
        details.append(f"Allowed values: `{markdown_text(', '.join(map(str, schema['enum'])))}`")
    example = first_example(schema.get("example", schema.get("examples")))
    if example is not None:
        details.append(f"Example: `{markdown_text(example)}`")
    if description and include_description:
        details.append(markdown_text(description))
    return "; ".join(details)


def sample_value(
    schema: dict[str, Any],
    components: dict[str, Any],
    field_name: str = "",
    definitions: dict[str, Any] | None = None,
) -> Any:
    definitions = definitions or {}
    reference = schema.get("$ref")
    if reference:
        name = reference.rsplit("/", 1)[-1]
        referenced = components.get(name, definitions.get(name, {}))
        return sample_value(referenced, components, field_name, definitions)

    if "allOf" in schema:
        combined: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
        for part in schema["allOf"]:
            resolved = part
            if "$ref" in part:
                name = part["$ref"].rsplit("/", 1)[-1]
                resolved = components.get(name, definitions.get(name, {}))
            combined["properties"].update(resolved.get("properties", {}))
            combined["required"].extend(resolved.get("required", []))
        return sample_value(combined, components, field_name, definitions)

    example = schema.get("example", schema.get("examples"))
    example = first_example(example)
    if example is not None:
        return example
    if "enum" in schema:
        return schema["enum"][0]
    if field_name in SAMPLE_VALUES:
        return SAMPLE_VALUES[field_name]

    for union in ("anyOf", "oneOf"):
        if union in schema:
            options = [
                option
                for option in schema[union]
                if option.get("type") != "null"
                and not (
                    option.get("$ref", "").endswith("/NoneType")
                )
            ]
            if not options:
                return None
            return sample_value(options[0], components, field_name, definitions)

    if "default" in schema:
        return schema["default"]

    if schema.get("type") == "object" or "properties" in schema:
        properties = schema.get("properties", {})
        required = set(schema.get("required", []))
        result = {
            name: sample_value(value, components, name, definitions)
            if name in required or value.get("type") != "null"
            else None
            for name, value in properties.items()
        }
        if field_name == "admission" and "status" in result:
            result["status"] = "submitted"
        return result

    if schema.get("type") == "array":
        count = max(1, schema.get("minItems", 0))
        return [
            sample_value(schema.get("items", {}), components, field_name, definitions)
            for _ in range(count)
        ]

    schema_type_name = schema.get("type")
    if isinstance(schema_type_name, list):
        schema_type_name = next(
            (value for value in schema_type_name if value != "null"),
            "null",
        )
    fmt = schema.get("format")
    if schema_type_name == "string":
        if fmt == "email":
            return "person@example.com"
        if fmt == "date":
            return "2026-10-20"
        if fmt == "time":
            return "10:30:00"
        if fmt == "date-time":
            return "2026-10-20T10:00:00Z"
        if field_name.endswith("_id") or field_name in {"id", "class_id"}:
            return "EXAMPLE-CODE"
        return f"Example {field_name.replace('_', ' ')}".strip()
    if schema_type_name == "integer":
        return 1
    if schema_type_name == "number":
        return 1.0
    if schema_type_name == "boolean":
        return True
    if schema_type_name == "null":
        return None
    return {}


def request_example(schema: dict[str, Any], components: dict[str, Any]) -> Any:
    return sample_value(schema, components)


def endpoint_handler_names() -> dict[tuple[str, str], str]:
    handlers = {}
    for route in app.routes:
        path = getattr(route, "path", "")
        endpoint = getattr(route, "endpoint", None)
        if not endpoint:
            continue
        for method in getattr(route, "methods", set()):
            if method.lower() in HTTP_METHODS:
                handlers[(path, method.lower())] = endpoint.__name__
    return handlers


def response_example(
    handler: str,
    method: str,
    components: dict[str, Any],
) -> tuple[dict[str, Any] | None, str | None]:
    model_info = RESPONSE_MODELS.get(handler)
    custom_data = CUSTOM_RESPONSE_DATA.get(handler)
    if model_info:
        model_name, paginated = model_info
        model = MODEL_REGISTRY.get(model_name)
        if not model:
            return None, f"Response model `{model_name}` could not be loaded."
        model_schema = model.model_json_schema()
        definitions = model_schema.pop("$defs", {})
        data = sample_value(model_schema, components, definitions=definitions)
        data.update(MODEL_FIELD_EXAMPLES.get(model_name, {}))
        data.update(HANDLER_FIELD_EXAMPLES.get(handler, {}))
        if paginated:
            data = [data]
    elif custom_data:
        data, paginated = custom_data
    else:
        return None, (
            "The handler does not have a declared response model in OpenAPI; "
            "its exact data structure must be checked in the route implementation."
        )

    message = success_message(handler) or {
        "POST": "Operation completed successfully",
        "PUT": "Operation completed successfully",
        "DELETE": "Operation completed successfully",
        "GET": "Records fetched successfully",
    }.get(method.upper(), "Operation completed successfully")
    result: dict[str, Any] = {
        "success": True,
        "message": message,
        "data": data,
        "meta": {
            "request_id": "example-request-id",
            "timestamp": "2026-10-20T10:00:00Z",
        },
    }
    if paginated:
        result["pagination"] = {
            "page": 1,
            "limit": 10,
            "total_records": len(data),
            "total_pages": 1 if data else 0,
        }
    return result, None


def success_message(handler_name: str) -> str | None:
    handler = next(
        (
            route.endpoint
            for route in app.routes
            if getattr(route, "endpoint", None)
            and route.endpoint.__name__ == handler_name
        ),
        None,
    )
    if handler is None:
        return None
    try:
        source = ast.parse(inspect.getsource(handler))
    except (OSError, SyntaxError):
        return None
    for node in ast.walk(source):
        if not isinstance(node, ast.Call):
            continue
        called_name = (
            node.func.id
            if isinstance(node.func, ast.Name)
            else node.func.attr
            if isinstance(node.func, ast.Attribute)
            else ""
        )
        if called_name == "success_response" and node.args:
            message = node.args[0]
            if isinstance(message, ast.Constant) and isinstance(message.value, str):
                return message.value
    return None


def render_parameter(parameter: dict[str, Any]) -> str:
    schema = parameter.get("schema", {})
    parameter_examples = parameter.get("example", parameter.get("examples"))
    schema_examples = schema.get("example", schema.get("examples"))
    example = first_example(parameter_examples or schema_examples)
    details = operation_schema(schema, include_description=False)
    if example is not None and "Example:" not in details:
        details += f"; Example: `{markdown_text(example)}`"
    descriptions = {
        "class_id": "Numeric database ID of the class.",
        "subject_id": "Numeric database ID of the subject.",
        "teacher_id": "Numeric database ID of the teacher.",
        "student_id": "Numeric database ID of the student.",
    }
    description = parameter.get("description") or descriptions.get(parameter["name"], "—")
    return (
        f"| `{markdown_text(parameter['name'])}` "
        f"| {markdown_text(parameter.get('in', ''))} "
        f"| {'Yes' if parameter.get('required') else 'No'} "
        f"| {details} "
        f"| {markdown_text(description)} |"
    )


def response_schema(response: dict[str, Any]) -> str:
    content = response.get("content", {})
    if not content:
        return "—"
    schemas = []
    for media_type, media in content.items():
        schema = media.get("schema", {})
        schemas.append(f"`{media_type}`: {schema_type(schema)}")
    return "; ".join(schemas)


def authorization_requirement(handler_name: str | None) -> str:
    if not handler_name:
        return "Not available from the route handler."
    handler = next(
        (
            route.endpoint
            for route in app.routes
            if getattr(route, "endpoint", None)
            and route.endpoint.__name__ == handler_name
        ),
        None,
    )
    if handler is None:
        return "Not available from the route handler."
    try:
        source = ast.parse(inspect.getsource(handler))
    except (OSError, SyntaxError):
        return "Not available from the route handler."

    permissions = []
    roles = []
    authenticated = False
    for node in ast.walk(source):
        if not isinstance(node, ast.Call):
            continue
        called_name = (
            node.func.id
            if isinstance(node.func, ast.Name)
            else node.func.attr
            if isinstance(node.func, ast.Attribute)
            else ""
        )
        if called_name == "require_permissions":
            permissions.extend(
                arg.value
                for arg in node.args
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
            )
        elif called_name == "require_roles":
            roles.extend(
                arg.value
                for arg in node.args
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str)
            )
        elif called_name == "get_current_user":
            authenticated = True

    if permissions:
        values = ", ".join(f"`{value}`" for value in permissions)
        return f"Requires permission {values}."
    if roles:
        values = ", ".join(f"`{value}`" for value in roles)
        return f"Requires one of these roles: {values}."
    if authenticated:
        return "Requires an authenticated active user (bearer access token)."
    return "Public route; no bearer token dependency declared."


def render_operation(
    path: str,
    method: str,
    operation: dict[str, Any],
    default_security: list[dict[str, Any]] | None,
    components: dict[str, Any],
    handlers: dict[tuple[str, str], str],
) -> list[str]:
    lines = [
        f"### `{method.upper()} {path}`",
        "",
        operation.get("summary", "Operation"),
        "",
    ]
    description = operation.get("description")
    if description:
        lines.extend([description, ""])
    tags = operation.get("tags", [])
    if tags:
        lines.extend([f"**Group:** {', '.join(f'`{tag}`' for tag in tags)}", ""])

    handler = handlers.get((path, method.lower()))
    security = operation.get("security", default_security)
    if security:
        schemes = sorted({name for requirement in security for name in requirement})
        value = ", ".join(f"`{name}`" for name in schemes) or "OpenAPI security requirement"
    elif security == []:
        value = "No authentication required"
    else:
        value = "Not specified by OpenAPI"
    lines.extend([f"**OpenAPI authentication:** {value}", ""])
    lines.extend(
        [f"**Authorization requirement:** {authorization_requirement(handler)}", ""]
    )

    parameters = operation.get("parameters", [])
    if parameters:
        lines.extend(
            [
                "**Parameters**",
                "",
                "| Name | Location | Required | Type and constraints | Description |",
                "|---|---|---:|---|---|",
            ]
        )
        lines.extend(render_parameter(parameter) for parameter in parameters)
        lines.append("")
    else:
        lines.extend(["**Parameters:** None.", ""])

    request_body = operation.get("requestBody")
    if request_body:
        lines.extend(["**Request body**", ""])
        if request_body.get("description"):
            lines.extend([request_body["description"], ""])
        lines.append(f"Required: {'Yes' if request_body.get('required') else 'No'}")
        for media_type, media in request_body.get("content", {}).items():
            lines.append(f"- `{media_type}`: {schema_type(media.get('schema', {}))}")
            if media_type == "application/json":
                example = request_example(media.get("schema", {}), components)
                lines.extend(
                    [
                        "",
                        "**Illustrative JSON request**",
                        "",
                        "```json",
                        json.dumps(example, indent=2, ensure_ascii=False),
                        "```",
                    ]
                )
            elif media_type == "multipart/form-data":
                lines.extend(
                    [
                        "",
                        "For multipart requests, send the listed fields as form parts. "
                        "The `file` part must contain the selected local file, not a "
                        "JSON-encoded path.",
                    ]
                )
        lines.append("")
    else:
        lines.extend(["**Request body:** Not used by this endpoint.", ""])

    success_status = next(
        (
            status_code
            for status_code in operation.get("responses", {})
            if status_code.startswith("2")
        ),
        None,
    )
    if success_status and handler:
        sample, note = response_example(
            handler,
            method,
            components,
        )
        lines.extend(["**Illustrative success response**", ""])
        if sample is not None:
            lines.extend(
                [
                    f"HTTP `{success_status}`. IDs, dates, request IDs, and tokens below "
                    "are illustrative; the token strings are not valid credentials.",
                    "",
                    "```json",
                    json.dumps(sample, indent=2, ensure_ascii=False),
                    "```",
                    "",
                ]
            )
        else:
            lines.extend([note or "Response example unavailable.", ""])

    lines.extend(
        [
            "**Responses**",
            "",
            "| HTTP status | Description | Response schema |",
            "|---:|---|---|",
        ]
    )
    for status, response in operation.get("responses", {}).items():
        body_schema = response_schema(response)
        if status == "422":
            body_schema = (
                "Standard API error envelope; see [HTTP 422 example]"
                "(#http-422-validation-error). The runtime handler replaces FastAPI's "
                "default validation-error body."
            )
        lines.append(
            f"| `{status}` | {markdown_text(response.get('description', '—'))} "
            f"| {body_schema} |"
        )
    lines.append("")
    if "422" in operation.get("responses", {}):
        lines.extend(
            [
                "**Validation failure example:** See "
                "[HTTP 422 error example](#http-422-validation-error). "
                "The exact error field/message depends on which path, query, header, form, "
                "or body rule failed.",
                "",
            ]
        )
    return lines


def render_component(name: str, schema: dict[str, Any]) -> list[str]:
    lines = [f"### `{name}`", ""]
    if schema.get("description"):
        lines.extend([schema["description"], ""])

    if schema.get("enum"):
        lines.extend(
            [
                "**Allowed values:** "
                + ", ".join(f"`{markdown_text(value)}`" for value in schema["enum"]),
                "",
            ]
        )

    properties = schema.get("properties", {})
    if properties:
        required = set(schema.get("required", []))
        lines.extend(
            [
                "| Property | Type | Required | Constraints | Description |",
                "|---|---|---:|---|---|",
            ]
        )
        for property_name, property_schema in properties.items():
            description = markdown_text(property_schema.get("description", "—"))
            example = first_example(
                property_schema.get("example", property_schema.get("examples"))
            )
            if example is not None:
                description += f"; Example: `{markdown_text(example)}`"
            lines.append(
                f"| `{markdown_text(property_name)}` "
                f"| {schema_type(property_schema)} "
                f"| {'Yes' if property_name in required else 'No'} "
                f"| {schema_constraints(property_schema)} "
                f"| {description} |"
            )
        lines.append("")
    elif not schema.get("enum"):
        lines.extend([f"**Type:** {schema_type(schema)}", ""])
    return lines


def main() -> None:
    spec = app.openapi()
    operations = [
        (path, method, operation)
        for path, path_item in spec["paths"].items()
        for method, operation in path_item.items()
        if method in HTTP_METHODS
    ]
    components = spec.get("components", {}).get("schemas", {})
    handlers = endpoint_handler_names()

    lines = [
        "# API Reference",
        "",
        "> Generated from the application's FastAPI OpenAPI schema. Regenerate after API "
        "changes with `python scripts/generate_api_reference.py`.",
        "",
        "The OpenAPI schema at `/openapi.json` and interactive `/docs` are the runtime "
        "contract. This file provides a browsable snapshot of every operation, its "
        "parameters, request and response schemas, and the field constraints exposed by "
        "OpenAPI. The shared response envelopes and route permissions are documented in "
        "[the technical guide](technical-documentation.md#8-authentication--authorization).",
        "",
        f"**Operations:** {len(operations)}",
        "",
        "## Operations",
        "",
    ]
    for path, method, operation in operations:
        lines.extend(
            render_operation(
                path,
                method,
                operation,
                spec.get("security"),
                components,
                handlers,
            )
        )

    lines.extend(
        [
            "## Common runtime error examples",
            "",
            "The exception handlers return the shared API error envelope. OpenAPI declares "
            "request validation status `422`, but it does not list every application "
            "exception status for every operation. The additional examples below describe "
            "runtime formats; whether a status applies depends on that route's validation, "
            "authentication, resource, and business rules.",
            "",
            "### HTTP 422 Validation error",
            "",
            "Invalid request data and business-rule violations both use HTTP 422; the "
            "`errors[].code` distinguishes ordinary input validation from a business rule.",
            "",
            "```json",
            json.dumps(
                {
                    "success": False,
                    "message": "Validation failed",
                    "data": None,
                    "errors": [
                        {
                            "code": "VALIDATION_ERROR",
                            "field": "body.email",
                            "message": "Invalid email address",
                        }
                    ],
                    "meta": {
                        "request_id": "example-request-id",
                        "timestamp": "2026-10-20T10:00:00Z",
                    },
                },
                indent=2,
            ),
            "```",
            "",
        ]
    )
    common_errors = [
        (
            "401 Authentication required",
            "AUTH_INVALID_CREDENTIALS",
            "Invalid credentials or token.",
        ),
        ("403 Permission denied", "AUTH_FORBIDDEN", "The user lacks route permission."),
        (
            "404 Resource not found",
            "RESOURCE_NOT_FOUND",
            "The requested record does not exist.",
        ),
        (
            "409 Resource conflict",
            "RESOURCE_CONFLICT",
            "A uniqueness or database constraint conflict occurred.",
        ),
        (
            "500 Internal server error",
            "INTERNAL_SERVER_ERROR",
            "An unexpected server error occurred.",
        ),
        (
            "503 Database unavailable",
            "DATABASE_UNAVAILABLE",
            "Database connection is unavailable",
        ),
    ]
    for heading, code, message in common_errors:
        http_status, label = heading.split(" ", 1)
        lines.extend(
            [
                f"### HTTP {http_status} {label}",
                "",
                "```json",
                json.dumps(
                    {
                        "success": False,
                        "message": (
                            "Service unavailable" if http_status == "503" else message
                        ),
                        "data": None,
                        "errors": [{"code": code, "message": message}],
                        "meta": {
                            "request_id": "example-request-id",
                            "timestamp": "2026-10-20T10:00:00Z",
                        },
                    },
                    indent=2,
                ),
                "```",
                "",
            ]
        )

    if components:
        lines.extend(["## Schemas", ""])
        lines.extend(
            [
                "Schema links above lead to these definitions. Required fields, types, "
                "constraints, enum values, descriptions, and available examples are "
                "rendered from the OpenAPI components.",
                "",
            ]
        )
        for name, schema in sorted(components.items()):
            lines.extend(render_component(name, schema))

    OUTPUT.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    print(
        f"Wrote {OUTPUT.relative_to(ROOT)} "
        f"({len(operations)} operations, {len(components)} schemas)"
    )


if __name__ == "__main__":
    main()
