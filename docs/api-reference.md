# API Reference

> Generated from the application's FastAPI OpenAPI schema. Regenerate after API changes with `python scripts/generate_api_reference.py`.

The OpenAPI schema at `/openapi.json` and interactive `/docs` are the runtime contract. This file provides a browsable snapshot of every operation, its parameters, request and response schemas, and the field constraints exposed by OpenAPI. The shared response envelopes and route permissions are documented in [the technical guide](technical-documentation.md#8-authentication--authorization).

**Operations:** 122

## Operations

### `GET /api/v1/public/student/classes`

List classes available for public admission applications

**Group:** `public`

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Available admission classes fetched successfully",
  "data": [
    {
      "id": 1,
      "name": "Grade 5",
      "section": "A",
      "academic_year": "2026-2027"
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |

### `POST /api/v1/public/student/inquiry`

Submit student admission inquiry

Public form submission. Returns inquiry_code for status tracking.

**Group:** `public`

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`PublicInquiryCreateRequest`](#publicinquirycreaterequest)

**Illustrative JSON request**

```json
{
  "first_name": "Aarav",
  "middle_name": null,
  "last_name": "Sharma",
  "gender": "male",
  "father_name": "Rohit Sharma",
  "dob": "2018-04-12",
  "student_mobile": null,
  "parent_mobile": "+919876543210",
  "email": "parent@example.com",
  "address": "12 School Road, Pune",
  "last_school": "Green Valley School",
  "current_class": "Grade 4",
  "admission_for_class": "Grade 5",
  "last_school_percentage": "87.50",
  "admission_for_class_id": 1
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Inquiry created successfully",
  "data": {
    "inquiry_code": "INQ202600007",
    "status": "PENDING"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/public/student/inquiry/status/{inquiry_code}`

Check inquiry status

Requires the parent email and mobile number submitted with the inquiry.

**Group:** `public`

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `inquiry_code` | path | Yes | string; Example: `INQ202600007` | Inquiry tracking code returned when the inquiry was submitted. |
| `X-Parent-Email` | header | Yes | string (email) | Email address supplied with the original inquiry. |
| `X-Parent-Mobile` | header | Yes | string | Parent/guardian mobile number supplied with the original inquiry. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Inquiry status fetched successfully",
  "data": {
    "inquiry_code": "INQ202600007",
    "status": "PENDING",
    "rejection_reason": "Required admission document is missing.",
    "admission_for_class": "Grade 5",
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z",
    "status_timeline": [
      {
        "id": 1,
        "from_status": "PENDING",
        "to_status": "UNDER_REVIEW",
        "change_reason": "Inquiry moved to staff review.",
        "created_at": "2026-10-20T10:00:00Z"
      }
    ],
    "latest_interview": {
      "schedule_date": "2026-11-05",
      "schedule_time": "10:30",
      "location": "Room 101",
      "mode": "OFFLINE",
      "result": "SCHEDULED"
    },
    "admission": {
      "admission_code": "ADM202600055",
      "status": "submitted",
      "documents_uploaded": 0,
      "documents_required": 6,
      "documents": [
        {
          "document_type": "Example document type",
          "verification_status": "Example verification status",
          "rejection_reason": "Required admission document is missing."
        }
      ],
      "student_code": "STU202600001",
      "student_name": "Example student name",
      "class_name": "Example class name",
      "section": "A",
      "academic_year": "2026-2027",
      "roll_number": 1
    }
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/public/student/inquiry/update`

Update inquiry details

Requires inquiry_code, email, and parent_mobile to verify ownership.

**Group:** `public`

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`PublicInquiryUpdateRequest`](#publicinquiryupdaterequest)

**Illustrative JSON request**

```json
{
  "inquiry_code": "INQ202600007",
  "email": "parent@example.com",
  "parent_mobile": "+919876543210",
  "first_name": "Aarav",
  "middle_name": null,
  "last_name": "Sharma",
  "gender": "male",
  "father_name": "Rohit Sharma",
  "dob": "2018-04-12",
  "student_mobile": null,
  "address": "12 School Road, Pune",
  "last_school": "Green Valley School",
  "current_class": "Grade 4",
  "admission_for_class": "Grade 5",
  "last_school_percentage": "87.50"
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Inquiry updated successfully",
  "data": {
    "inquiry_code": "INQ202600007",
    "status": "PENDING",
    "rejection_reason": "Required admission document is missing.",
    "admission_for_class": "Grade 5",
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z",
    "status_timeline": [
      {
        "id": 1,
        "from_status": "PENDING",
        "to_status": "UNDER_REVIEW",
        "change_reason": "Inquiry moved to staff review.",
        "created_at": "2026-10-20T10:00:00Z"
      }
    ],
    "latest_interview": {
      "schedule_date": "2026-11-05",
      "schedule_time": "10:30",
      "location": "Room 101",
      "mode": "OFFLINE",
      "result": "SCHEDULED"
    },
    "admission": {
      "admission_code": "ADM202600055",
      "status": "submitted",
      "documents_uploaded": 0,
      "documents_required": 6,
      "documents": [
        {
          "document_type": "Example document type",
          "verification_status": "Example verification status",
          "rejection_reason": "Required admission document is missing."
        }
      ],
      "student_code": "STU202600001",
      "student_name": "Example student name",
      "class_name": "Example class name",
      "section": "A",
      "academic_year": "2026-2027",
      "roll_number": 1
    }
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/public/student/admission`

Submit admission application (after interview pass)

Public admission form (FRD POST /student/admission).

Parent must verify via inquiry_code, email, and parent_mobile.

**Group:** `public`

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body**

Required: Yes
- `application/x-www-form-urlencoded`: [`Body_submit_admission_api_v1_public_student_admission_post`](#body_submit_admission_api_v1_public_student_admission_post)

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Admission submitted successfully",
  "data": {
    "admission_code": "ADM202600001",
    "status": "submitted"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/public/student/admission/documents`

Upload an admission document as the verified parent

**Group:** `public`

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body**

Required: Yes
- `multipart/form-data`: [`Body_upload_public_admission_document_api_v1_public_student_admission_documents_post`](#body_upload_public_admission_document_api_v1_public_student_admission_documents_post)

For multipart requests, send the listed fields as form parts. The `file` part must contain the selected local file, not a JSON-encoded path.

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Admission document uploaded successfully",
  "data": {
    "document_type": "Example document type",
    "verification_status": "Example verification status",
    "rejection_reason": "Required admission document is missing.",
    "verified_at": "2026-10-20T10:00:00Z"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/public/student/inquiry/status/{inquiry_code}/admission-letter`

Download the admission letter after enrollment

**Group:** `public`

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `inquiry_code` | path | Yes | string | — |
| `X-Parent-Email` | header | Yes | string (email) | — |
| `X-Parent-Mobile` | header | Yes | string | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

This endpoint returns a binary PDF file; no JSON success envelope is returned.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Parent-verified PDF admission letter. | `application/pdf`: string (binary) |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/public/events`

List Public Events

**Group:** `public`, `public`

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |

### `GET /api/v1/teachers/me/class-subjects`

List My Teaching Assignments

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teaching_assignments.manage`.

**Parameters:** None.

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |

### `POST /api/v1/teachers/me/class-subjects`

Add My Teaching Assignment

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teaching_assignments.manage`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | query | Yes | integer | Numeric database ID of the class. |
| `subject_id` | query | Yes | integer | Numeric database ID of the subject. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `DELETE /api/v1/teachers/me/class-subjects/{class_id}/{subject_id}`

Remove My Teaching Assignment

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teaching_assignments.manage`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | path | Yes | integer | Numeric database ID of the class. |
| `subject_id` | path | Yes | integer | Numeric database ID of the subject. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/assignments`

List Assignments

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `assignments.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | query | No | anyOf: integer, null | Numeric database ID of the class. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/assignments`

Create Assignment

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `assignments.create`.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`AssignmentCreateRequest`](#assignmentcreaterequest)

**Illustrative JSON request**

```json
{
  "title": "Example title",
  "details": "Example details",
  "class_id": 1,
  "subject_id": 1,
  "teacher_id": 1,
  "assigned_date": "2026-10-20",
  "due_date": "2026-10-20"
}
```

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/assignments/{assignment_id}`

Get Assignment

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `assignments.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `assignment_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/assignments/{assignment_id}`

Update Assignment

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `assignments.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `assignment_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `application/json`: [`AssignmentUpdateRequest`](#assignmentupdaterequest)

**Illustrative JSON request**

```json
{
  "title": "Example title",
  "details": "Example details",
  "due_date": "2026-10-20"
}
```

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/assignments/{assignment_id}/publish`

Publish Assignment

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `assignments.publish`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `assignment_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/assignments/{assignment_id}/close`

Close Assignment

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `assignments.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `assignment_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/assignments/{assignment_id}/attachments`

Upload Assignment Attachment

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `assignments.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `assignment_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `multipart/form-data`: [`Body_upload_assignment_attachment_api_v1_assignments__assignment_id__attachments_post`](#body_upload_assignment_attachment_api_v1_assignments__assignment_id__attachments_post)

For multipart requests, send the listed fields as form parts. The `file` part must contain the selected local file, not a JSON-encoded path.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/assignments/{assignment_id}/attachments/{attachment_id}`

Download Assignment Attachment

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `assignments.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `assignment_id` | path | Yes | integer | — |
| `attachment_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/timetable`

List Timetable

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `timetable.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | query | No | anyOf: integer, null | Numeric database ID of the class. |
| `academic_year` | query | No | anyOf: string, null | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/timetable`

Create Timetable Entry

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `timetable.create`.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`TimetableCreateRequest`](#timetablecreaterequest)

**Illustrative JSON request**

```json
{
  "class_id": 1,
  "subject_id": 1,
  "teacher_id": 1,
  "day_of_week": 1,
  "start_time": "10:30:00",
  "end_time": "10:30:00",
  "room": "Example room",
  "academic_year": "2026-2027"
}
```

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/timetable/{entry_id}`

Update Timetable Entry

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `timetable.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `entry_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `application/json`: [`TimetableUpdateRequest`](#timetableupdaterequest)

**Illustrative JSON request**

```json
{
  "class_id": 1,
  "subject_id": 1,
  "teacher_id": 1,
  "day_of_week": 1,
  "start_time": "10:30:00",
  "end_time": "10:30:00",
  "room": "Example room",
  "academic_year": "2026-2027"
}
```

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/assessments`

List Assessments

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `assessments.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | query | No | anyOf: integer, null | Numeric database ID of the class. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/assessments`

Create Assessment

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `assessments.create`.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`AssessmentCreateRequest`](#assessmentcreaterequest)

**Illustrative JSON request**

```json
{
  "name": "Grade 5",
  "assessment_type": "unit_test",
  "class_id": 1,
  "subject_id": 1,
  "teacher_id": 1,
  "assessment_date": "2026-10-20",
  "max_score": 1.0
}
```

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/assessments/{assessment_id}`

Get Assessment

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `assessments.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `assessment_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/assessments/{assessment_id}`

Update Assessment

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `assessments.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `assessment_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `application/json`: [`AssessmentUpdateRequest`](#assessmentupdaterequest)

**Illustrative JSON request**

```json
{
  "name": "Grade 5",
  "assessment_type": "unit_test",
  "assessment_date": "2026-10-20",
  "max_score": 1.0
}
```

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/assessments/{assessment_id}/results/{student_id}`

Upsert Assessment Result

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `assessments.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `assessment_id` | path | Yes | integer | — |
| `student_id` | path | Yes | integer | Numeric database ID of the student. |

**Request body**

Required: Yes
- `application/json`: [`AssessmentResultRequest`](#assessmentresultrequest)

**Illustrative JSON request**

```json
{
  "score": 1.0,
  "result_status": "present",
  "remarks": "Please bring the previous report card."
}
```

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/assessments/{assessment_id}/publish`

Publish Assessment

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `assessments.publish`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `assessment_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/events`

List Events

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `events.read`.

**Parameters:** None.

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |

### `POST /api/v1/events`

Create Event

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `events.create`.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`EventCreateRequest`](#eventcreaterequest)

**Illustrative JSON request**

```json
{
  "title": "Example title",
  "description": "Example description",
  "starts_at": "2026-10-20T10:00:00Z",
  "ends_at": "2026-10-20T10:00:00Z",
  "venue": "Example venue",
  "audience": "public"
}
```

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/events/{event_id}`

Update Event

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `events.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `event_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `application/json`: [`EventUpdateRequest`](#eventupdaterequest)

**Illustrative JSON request**

```json
{
  "title": "Example title",
  "description": "Example description",
  "starts_at": "2026-10-20T10:00:00Z",
  "ends_at": "2026-10-20T10:00:00Z",
  "venue": "Example venue",
  "audience": "public"
}
```

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/events/{event_id}/review`

Review Event

**Group:** `role portals`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `events.review`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `event_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `application/json`: [`EventReviewRequest`](#eventreviewrequest)

**Illustrative JSON request**

```json
{
  "status": "published",
  "rejection_reason": "Required admission document is missing."
}
```

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/auth/student/register`

Register Student Portal

**Group:** `auth`

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`StudentPortalRegistrationRequest`](#studentportalregistrationrequest)

**Illustrative JSON request**

```json
{
  "admission_id": "EXAMPLE-CODE",
  "email": "parent@example.com",
  "password": "ExamplePassword!2026",
  "confirm_password": "Example confirm password"
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Student portal account created. You can now sign in with your student ID.",
  "data": {
    "student_id": 1,
    "email": "parent@example.com"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/auth/student/login`

Login Student Portal

**Group:** `auth`

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`StudentPortalLoginRequest`](#studentportalloginrequest)

**Illustrative JSON request**

```json
{
  "student_id": 1,
  "password": "ExamplePassword!2026"
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "example-access-token-not-valid",
    "refresh_token": "example-refresh-token-not-valid",
    "token_type": "bearer",
    "expires_in": 1
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/auth/register`

Register User

**Group:** `auth`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires one of these roles: `SUPER_ADMIN`, `ADMIN`.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`UserRegisterRequest`](#userregisterrequest)

**Illustrative JSON request**

```json
{
  "first_name": "Aarav",
  "last_name": "Sharma",
  "email": "parent@example.com",
  "phone": "+919876543211",
  "password": "ExamplePassword!2026",
  "role_codes": [
    "TEACHER"
  ]
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "id": 1,
    "email": "parent@example.com",
    "roles": [
      "TEACHER"
    ],
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/auth/login`

Login User

**Group:** `auth`

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`LoginRequest`](#loginrequest)

**Illustrative JSON request**

```json
{
  "email": "parent@example.com",
  "password": "ExamplePassword!2026",
  "portal": "student"
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "example-access-token-not-valid",
    "refresh_token": "example-refresh-token-not-valid",
    "token_type": "bearer",
    "expires_in": 1
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/auth/refresh-token`

Refresh Token

**Group:** `auth`

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`RefreshTokenRequest`](#refreshtokenrequest)

**Illustrative JSON request**

```json
{
  "refresh_token": "example-refresh-token-not-valid"
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "example-access-token-not-valid",
    "token_type": "bearer",
    "expires_in": 1
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/auth/me`

Get Me

**Group:** `auth`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "User fetched successfully",
  "data": {
    "id": 1,
    "first_name": "Aarav",
    "last_name": "Sharma",
    "email": "parent@example.com",
    "phone": "+919876543211",
    "roles": [
      "TEACHER"
    ],
    "permissions": [
      "teachers.read"
    ],
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |

### `POST /api/v1/auth/change-password`

Change Password

**Group:** `auth`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`ChangePasswordRequest`](#changepasswordrequest)

**Illustrative JSON request**

```json
{
  "current_password": "ExampleCurrentPassword!2026",
  "new_password": "ExampleNewPassword!2026"
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Password changed successfully",
  "data": null,
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/auth/logout`

Logout User

**Group:** `auth`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`LogoutRequest`](#logoutrequest)

**Illustrative JSON request**

```json
{
  "refresh_token": "example-refresh-token-not-valid"
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Logout successful",
  "data": null,
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/auth/verify-token`

Verify Token

**Group:** `auth`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Token is valid",
  "data": {
    "valid": true,
    "user_id": 1
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |

### `POST /api/v1/classes/`

Create Class

**Group:** `classes`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `classes.create`.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`ClassCreateRequest`](#classcreaterequest)

**Illustrative JSON request**

```json
{
  "name": "Grade 5",
  "section": "A",
  "academic_year": "2026-2027",
  "capacity": 1
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Class created successfully",
  "data": {
    "id": 1,
    "class_teacher_id": 1,
    "name": "Grade 5",
    "section": "A",
    "academic_year": "2026-2027",
    "capacity": 1,
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/classes/`

List Classes

**Group:** `classes`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `classes.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `academic_year` | query | No | anyOf: string, null; Example: `2026-2027` | Filter by academic year. |
| `status` | query | No | anyOf: [`ClassStatus`](#classstatus), null | Filter by class state: active or inactive. |
| `page` | query | No | integer | 1-based page number to return. |
| `limit` | query | No | integer | Number of records per page, from 1 to 100. |
| `sort_by` | query | No | string | Field used to sort results; supported fields depend on the endpoint. |
| `sort_order` | query | No | string; Allowed values: `asc, desc` | Sort direction: asc or desc. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Records fetched successfully",
  "data": [
    {
      "id": 1,
      "class_teacher_id": 1,
      "name": "Grade 5",
      "section": "A",
      "academic_year": "2026-2027",
      "capacity": 1,
      "status": "active"
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  },
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_records": 1,
    "total_pages": 1
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/classes/{class_id}`

Get Class

**Group:** `classes`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `classes.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | path | Yes | integer | Numeric database ID of the class. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Class fetched successfully",
  "data": {
    "id": 1,
    "class_teacher_id": 1,
    "name": "Grade 5",
    "section": "A",
    "academic_year": "2026-2027",
    "capacity": 1,
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/classes/{class_id}`

Update Class

**Group:** `classes`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `classes.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | path | Yes | integer | Numeric database ID of the class. |

**Request body**

Required: Yes
- `application/json`: [`ClassUpdateRequest`](#classupdaterequest)

**Illustrative JSON request**

```json
{
  "name": "Grade 5",
  "section": "A",
  "academic_year": "2026-2027",
  "capacity": 1,
  "status": "active"
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Class updated successfully",
  "data": {
    "id": 1,
    "class_teacher_id": 1,
    "name": "Grade 5",
    "section": "A",
    "academic_year": "2026-2027",
    "capacity": 1,
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `DELETE /api/v1/classes/{class_id}`

Delete Class

**Group:** `classes`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `classes.delete`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | path | Yes | integer | Numeric database ID of the class. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Class deleted successfully",
  "data": null,
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/classes/{class_id}/readiness`

Get Class Academic Readiness

**Group:** `classes`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `classes.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | path | Yes | integer | Numeric database ID of the class. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Class academic readiness fetched successfully",
  "data": {
    "class_id": 1,
    "ready": true,
    "class_teacher_id": 1,
    "active_subject_ids": [
      1
    ],
    "issues": []
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/classes/{class_id}/subjects`

List Class Subjects

**Group:** `classes`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `classes.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | path | Yes | integer | Numeric database ID of the class. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Class subjects fetched successfully",
  "data": [
    {
      "id": 1,
      "code": "MATH",
      "name": "Mathematics",
      "is_active": true
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/classes/{class_id}/subjects`

Assign Class Subject

**Group:** `classes`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `classes.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | path | Yes | integer | Numeric database ID of the class. |

**Request body**

Required: Yes
- `application/json`: [`ClassSubjectAssignRequest`](#classsubjectassignrequest)

**Illustrative JSON request**

```json
{
  "subject_id": 1
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Subject assigned to class successfully",
  "data": {
    "class_id": 1,
    "subject_id": 1
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `DELETE /api/v1/classes/{class_id}/subjects/{subject_id}`

Remove Class Subject

**Group:** `classes`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `classes.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | path | Yes | integer | Numeric database ID of the class. |
| `subject_id` | path | Yes | integer | Numeric database ID of the subject. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Subject removed from class successfully",
  "data": null,
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/classes/{class_id}/class-teacher`

Assign Class Teacher

**Group:** `classes`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `classes.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | path | Yes | integer | Numeric database ID of the class. |

**Request body**

Required: Yes
- `application/json`: [`ClassTeacherAssignRequest`](#classteacherassignrequest)

**Illustrative JSON request**

```json
{
  "teacher_id": 1
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Class teacher assigned successfully",
  "data": {
    "class_id": 1,
    "teacher_id": 1
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/classes/{class_id}/class-teacher`

Replace Class Teacher

**Group:** `classes`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `classes.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | path | Yes | integer | Numeric database ID of the class. |

**Request body**

Required: Yes
- `application/json`: [`ClassTeacherAssignRequest`](#classteacherassignrequest)

**Illustrative JSON request**

```json
{
  "teacher_id": 1
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Class teacher updated successfully",
  "data": {
    "class_id": 1,
    "teacher_id": 1
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `DELETE /api/v1/classes/{class_id}/class-teacher`

Remove Class Teacher

**Group:** `classes`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `classes.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | path | Yes | integer | Numeric database ID of the class. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Class teacher removed successfully",
  "data": null,
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/dashboard/summary`

Get permission-filtered dashboard metrics

**Group:** `dashboard`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires at least one of these permissions: `students.read`, `teachers.read`, `classes.read`, `subjects.read`, `inquiries.read`, `admissions.read`, `interviews.read`.

**Parameters:** None.

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Dashboard summary fetched successfully",
  "data": {
    "school_timezone": "Asia/Kolkata",
    "student_count": 1,
    "teacher_count": 1,
    "class_count": 1,
    "subject_count": 1,
    "inquiry_count": 1,
    "pending_admission_count": 1,
    "admissions_by_status": {
      "draft": 1,
      "submitted": 1,
      "document_pending": 1,
      "document_verification": 1,
      "approved": 1,
      "rejected": 1
    },
    "upcoming_interview_count": 1,
    "upcoming_interviews": [
      {
        "id": 1,
        "inquiry_code": "INQ202600007",
        "student_name": "Example student name",
        "schedule_date": "2026-11-05",
        "schedule_time": "10:30:00",
        "location": "Room 101",
        "mode": "OFFLINE"
      }
    ],
    "MonthlyFeeStructureResponse": {
      "components": [
        {
          "id": 1,
          "fee_name": "Tuition",
          "amount": 100.0,
          "billing_frequency": "MONTHLY",
          "is_optional": false,
          "description": null,
          "created_at": "2026-10-20T10:00:00Z"
        },
        {
          "id": 2,
          "fee_name": "Activity",
          "amount": 500.0,
          "billing_frequency": "ONE_TIME",
          "is_optional": true,
          "description": null,
          "created_at": "2026-10-20T10:00:00Z"
        }
      ],
      "mandatory_annual_total": 1200.0,
      "optional_annual_total": 500.0,
      "mandatory_monthly_equivalent": 100.0,
      "optional_monthly_equivalent": 41.67,
      "total_annual_amount": 1700.0
    }
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: [`DashboardSummaryEnvelope`](#dashboardsummaryenvelope) |

### `POST /api/v1/fees/admission-structures`

Create an admission fee structure

**Group:** `fees`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `fees.create`.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`AdmissionFeeStructureCreate`](#admissionfeestructurecreate)

**Illustrative JSON request**

```json
{
  "academic_year": "2026-2027",
  "class_id": 1,
  "structure_name": "Example structure name",
  "description": "Example description",
  "is_active": true,
  "components": [
    {
      "fee_name": "Example fee name",
      "amount": 1.0,
      "is_refundable": false,
      "is_optional": false,
      "description": "Example description"
    }
  ]
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Admission fee structure created successfully.",
  "data": {
    "id": 1,
    "academic_year": "2026-2027",
    "class_id": 1,
    "school_class": {
      "id": 1,
      "name": "Grade 5",
      "section": "A",
      "academic_year": "2026-2027"
    },
    "structure_name": "Example structure name",
    "description": "Example description",
    "is_active": true,
    "components": [
      {
        "id": 1,
        "fee_name": "Registration",
        "amount": 100.0,
        "is_refundable": false,
        "is_optional": false,
        "description": null,
        "created_at": "2026-10-20T10:00:00Z"
      },
      {
        "id": 2,
        "fee_name": "Uniform",
        "amount": 20.0,
        "is_refundable": false,
        "is_optional": true,
        "description": null,
        "created_at": "2026-10-20T10:00:00Z"
      }
    ],
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z",
    "mandatory_total": 100.0,
    "optional_total": 20.0,
    "total_amount": 120.0
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/fees/admission-structures`

List admission fee structures

**Group:** `fees`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `fees.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | query | No | anyOf: integer, null | Filter by class ID. |
| `academic_year` | query | No | anyOf: string, null | Filter by class academic year. |
| `is_active` | query | No | anyOf: boolean, null | Filter by active status. |
| `page` | query | No | integer | 1-based page number to return. |
| `limit` | query | No | integer | Number of records per page, from 1 to 100. |
| `sort_by` | query | No | string | Field used to sort results; supported fields depend on the endpoint. |
| `sort_order` | query | No | string; Allowed values: `asc, desc` | Sort direction: asc or desc. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Records fetched successfully",
  "data": [
    {
      "id": 1,
      "academic_year": "2026-2027",
      "class_id": 1,
      "school_class": {
        "id": 1,
        "name": "Grade 5",
        "section": "A",
        "academic_year": "2026-2027"
      },
      "structure_name": "Example structure name",
      "description": "Example description",
      "is_active": true,
      "components": [
        {
          "id": 1,
          "fee_name": "Registration",
          "amount": 100.0,
          "is_refundable": false,
          "is_optional": false,
          "description": null,
          "created_at": "2026-10-20T10:00:00Z"
        },
        {
          "id": 2,
          "fee_name": "Uniform",
          "amount": 20.0,
          "is_refundable": false,
          "is_optional": true,
          "description": null,
          "created_at": "2026-10-20T10:00:00Z"
        }
      ],
      "created_at": "2026-10-20T10:00:00Z",
      "updated_at": "2026-10-20T10:00:00Z",
      "mandatory_total": 100.0,
      "optional_total": 20.0,
      "total_amount": 120.0
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  },
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_records": 1,
    "total_pages": 1
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/fees/admission-structures/{structure_id}`

Get an admission fee structure

**Group:** `fees`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `fees.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `structure_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Admission fee structure fetched successfully.",
  "data": {
    "id": 1,
    "academic_year": "2026-2027",
    "class_id": 1,
    "school_class": {
      "id": 1,
      "name": "Grade 5",
      "section": "A",
      "academic_year": "2026-2027"
    },
    "structure_name": "Example structure name",
    "description": "Example description",
    "is_active": true,
    "components": [
      {
        "id": 1,
        "fee_name": "Registration",
        "amount": 100.0,
        "is_refundable": false,
        "is_optional": false,
        "description": null,
        "created_at": "2026-10-20T10:00:00Z"
      },
      {
        "id": 2,
        "fee_name": "Uniform",
        "amount": 20.0,
        "is_refundable": false,
        "is_optional": true,
        "description": null,
        "created_at": "2026-10-20T10:00:00Z"
      }
    ],
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z",
    "mandatory_total": 100.0,
    "optional_total": 20.0,
    "total_amount": 120.0
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/fees/admission-structures/{structure_id}`

Update an admission fee structure

**Group:** `fees`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `fees.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `structure_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `application/json`: [`AdmissionFeeStructureUpdate`](#admissionfeestructureupdate)

**Illustrative JSON request**

```json
{
  "academic_year": "2026-2027",
  "class_id": 1,
  "structure_name": "Example structure name",
  "description": "Example description",
  "is_active": true,
  "components": [
    {
      "id": 1,
      "fee_name": "Example fee name",
      "amount": 1.0,
      "is_refundable": true,
      "is_optional": true,
      "description": "Example description"
    }
  ]
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Admission fee structure updated successfully.",
  "data": {
    "id": 1,
    "academic_year": "2026-2027",
    "class_id": 1,
    "school_class": {
      "id": 1,
      "name": "Grade 5",
      "section": "A",
      "academic_year": "2026-2027"
    },
    "structure_name": "Example structure name",
    "description": "Example description",
    "is_active": true,
    "components": [
      {
        "id": 1,
        "fee_name": "Registration",
        "amount": 100.0,
        "is_refundable": false,
        "is_optional": false,
        "description": null,
        "created_at": "2026-10-20T10:00:00Z"
      },
      {
        "id": 2,
        "fee_name": "Uniform",
        "amount": 20.0,
        "is_refundable": false,
        "is_optional": true,
        "description": null,
        "created_at": "2026-10-20T10:00:00Z"
      }
    ],
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z",
    "mandatory_total": 100.0,
    "optional_total": 20.0,
    "total_amount": 120.0
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `DELETE /api/v1/fees/admission-structures/{structure_id}`

Deactivate an admission fee structure

**Group:** `fees`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `fees.delete`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `structure_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Admission fee structure deactivated.",
  "data": {
    "id": 1,
    "academic_year": "2026-2027",
    "class_id": 1,
    "school_class": {
      "id": 1,
      "name": "Grade 5",
      "section": "A",
      "academic_year": "2026-2027"
    },
    "structure_name": "Example structure name",
    "description": "Example description",
    "is_active": true,
    "components": [
      {
        "id": 1,
        "fee_name": "Registration",
        "amount": 100.0,
        "is_refundable": false,
        "is_optional": false,
        "description": null,
        "created_at": "2026-10-20T10:00:00Z"
      },
      {
        "id": 2,
        "fee_name": "Uniform",
        "amount": 20.0,
        "is_refundable": false,
        "is_optional": true,
        "description": null,
        "created_at": "2026-10-20T10:00:00Z"
      }
    ],
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z",
    "mandatory_total": 100.0,
    "optional_total": 20.0,
    "total_amount": 120.0
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PATCH /api/v1/fees/admission-structures/{structure_id}/status`

Change an admission fee structure's active status

**Group:** `fees`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `fees.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `structure_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `application/json`: [`FeeStructureStatusUpdate`](#feestructurestatusupdate)

**Illustrative JSON request**

```json
{
  "is_active": true
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Admission fee structure status updated.",
  "data": {
    "id": 1,
    "academic_year": "2026-2027",
    "class_id": 1,
    "school_class": {
      "id": 1,
      "name": "Grade 5",
      "section": "A",
      "academic_year": "2026-2027"
    },
    "structure_name": "Example structure name",
    "description": "Example description",
    "is_active": true,
    "components": [
      {
        "id": 1,
        "fee_name": "Registration",
        "amount": 100.0,
        "is_refundable": false,
        "is_optional": false,
        "description": null,
        "created_at": "2026-10-20T10:00:00Z"
      },
      {
        "id": 2,
        "fee_name": "Uniform",
        "amount": 20.0,
        "is_refundable": false,
        "is_optional": true,
        "description": null,
        "created_at": "2026-10-20T10:00:00Z"
      }
    ],
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z",
    "mandatory_total": 100.0,
    "optional_total": 20.0,
    "total_amount": 120.0
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/fees/monthly-structures`

Create a monthly fee structure

**Group:** `fees`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `fees.create`.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`MonthlyFeeStructureCreate`](#monthlyfeestructurecreate)

**Illustrative JSON request**

```json
{
  "academic_year": "2026-2027",
  "class_id": 1,
  "structure_name": "Example structure name",
  "description": "Example description",
  "is_active": true,
  "components": [
    {
      "fee_name": "Example fee name",
      "amount": 1.0,
      "billing_frequency": "MONTHLY",
      "is_optional": false,
      "description": "Example description"
    }
  ]
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Monthly fee structure created successfully.",
  "data": {
    "id": 1,
    "academic_year": "2026-2027",
    "class_id": 1,
    "school_class": {
      "id": 1,
      "name": "Grade 5",
      "section": "A",
      "academic_year": "2026-2027"
    },
    "structure_name": "Example structure name",
    "description": "Example description",
    "is_active": true,
    "components": [
      {
        "id": 1,
        "fee_name": "Example fee name",
        "amount": 1.0,
        "billing_frequency": "MONTHLY",
        "is_optional": true,
        "description": "Example description",
        "created_at": "2026-10-20T10:00:00Z"
      }
    ],
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/fees/monthly-structures`

List monthly fee structures

**Group:** `fees`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `fees.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `class_id` | query | No | anyOf: integer, null | Filter by class ID. |
| `academic_year` | query | No | anyOf: string, null | Filter by class academic year. |
| `is_active` | query | No | anyOf: boolean, null | Filter by active status. |
| `page` | query | No | integer | 1-based page number to return. |
| `limit` | query | No | integer | Number of records per page, from 1 to 100. |
| `sort_by` | query | No | string | Field used to sort results; supported fields depend on the endpoint. |
| `sort_order` | query | No | string; Allowed values: `asc, desc` | Sort direction: asc or desc. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Records fetched successfully",
  "data": [
    {
      "id": 1,
      "academic_year": "2026-2027",
      "class_id": 1,
      "school_class": {
        "id": 1,
        "name": "Grade 5",
        "section": "A",
        "academic_year": "2026-2027"
      },
      "structure_name": "Example structure name",
      "description": "Example description",
      "is_active": true,
      "components": [
        {
          "id": 1,
          "fee_name": "Example fee name",
          "amount": 1.0,
          "billing_frequency": "MONTHLY",
          "is_optional": true,
          "description": "Example description",
          "created_at": "2026-10-20T10:00:00Z"
        }
      ],
      "created_at": "2026-10-20T10:00:00Z",
      "updated_at": "2026-10-20T10:00:00Z"
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  },
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_records": 1,
    "total_pages": 1
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/fees/monthly-structures/{structure_id}`

Get a monthly fee structure

**Group:** `fees`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `fees.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `structure_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Monthly fee structure fetched successfully.",
  "data": {
    "id": 1,
    "academic_year": "2026-2027",
    "class_id": 1,
    "school_class": {
      "id": 1,
      "name": "Grade 5",
      "section": "A",
      "academic_year": "2026-2027"
    },
    "structure_name": "Example structure name",
    "description": "Example description",
    "is_active": true,
    "components": [
      {
        "id": 1,
        "fee_name": "Example fee name",
        "amount": 1.0,
        "billing_frequency": "MONTHLY",
        "is_optional": true,
        "description": "Example description",
        "created_at": "2026-10-20T10:00:00Z"
      }
    ],
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/fees/monthly-structures/{structure_id}`

Update a monthly fee structure

**Group:** `fees`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `fees.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `structure_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `application/json`: [`MonthlyFeeStructureUpdate`](#monthlyfeestructureupdate)

**Illustrative JSON request**

```json
{
  "academic_year": "2026-2027",
  "class_id": 1,
  "structure_name": "Example structure name",
  "description": "Example description",
  "is_active": true,
  "components": [
    {
      "id": 1,
      "fee_name": "Example fee name",
      "amount": 1.0,
      "billing_frequency": "MONTHLY",
      "is_optional": true,
      "description": "Example description"
    }
  ]
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Monthly fee structure updated successfully.",
  "data": {
    "id": 1,
    "academic_year": "2026-2027",
    "class_id": 1,
    "school_class": {
      "id": 1,
      "name": "Grade 5",
      "section": "A",
      "academic_year": "2026-2027"
    },
    "structure_name": "Example structure name",
    "description": "Example description",
    "is_active": true,
    "components": [
      {
        "id": 1,
        "fee_name": "Example fee name",
        "amount": 1.0,
        "billing_frequency": "MONTHLY",
        "is_optional": true,
        "description": "Example description",
        "created_at": "2026-10-20T10:00:00Z"
      }
    ],
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `DELETE /api/v1/fees/monthly-structures/{structure_id}`

Deactivate a monthly fee structure

**Group:** `fees`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `fees.delete`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `structure_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Monthly fee structure deactivated.",
  "data": {
    "id": 1,
    "academic_year": "2026-2027",
    "class_id": 1,
    "school_class": {
      "id": 1,
      "name": "Grade 5",
      "section": "A",
      "academic_year": "2026-2027"
    },
    "structure_name": "Example structure name",
    "description": "Example description",
    "is_active": true,
    "components": [
      {
        "id": 1,
        "fee_name": "Example fee name",
        "amount": 1.0,
        "billing_frequency": "MONTHLY",
        "is_optional": true,
        "description": "Example description",
        "created_at": "2026-10-20T10:00:00Z"
      }
    ],
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PATCH /api/v1/fees/monthly-structures/{structure_id}/status`

Change a monthly fee structure's active status

**Group:** `fees`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `fees.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `structure_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `application/json`: [`FeeStructureStatusUpdate`](#feestructurestatusupdate)

**Illustrative JSON request**

```json
{
  "is_active": true
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Monthly fee structure status updated.",
  "data": {
    "id": 1,
    "academic_year": "2026-2027",
    "class_id": 1,
    "school_class": {
      "id": 1,
      "name": "Grade 5",
      "section": "A",
      "academic_year": "2026-2027"
    },
    "structure_name": "Example structure name",
    "description": "Example description",
    "is_active": true,
    "components": [
      {
        "id": 1,
        "fee_name": "Example fee name",
        "amount": 1.0,
        "billing_frequency": "MONTHLY",
        "is_optional": true,
        "description": "Example description",
        "created_at": "2026-10-20T10:00:00Z"
      }
    ],
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/inquiries`

List Inquiries

Paginated list of all student inquiries for staff review.

**Group:** `inquiries`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `inquiries.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `status` | query | No | anyOf: string, null | Filter by status: PENDING, UNDER_REVIEW, PROCESSING, INTERVIEW_SCHEDULED, INTERVIEW_PASS, INTERVIEW_FAIL, DOCUMENT_PENDING, DOCUMENT_VERIFICATION, ADMISSION_SUCCESS, or REJECTED. |
| `admission_for_class_id` | query | No | anyOf: integer, null; Example: `1` | Filter by requested catalog class ID. |
| `search` | query | No | anyOf: string, null | Search by student name, inquiry code, email, or mobile. |
| `page` | query | No | integer | 1-based page number to return. |
| `limit` | query | No | integer | Number of records per page, from 1 to 100. |
| `sort_by` | query | No | string | Field used to sort results; supported fields depend on the endpoint. |
| `sort_order` | query | No | string; Allowed values: `asc, desc` | Sort direction: asc or desc. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Records fetched successfully",
  "data": [
    {
      "id": 1,
      "inquiry_code": "INQ202600007",
      "status_timeline": [],
      "serial_number": 1,
      "first_name": "Aarav",
      "middle_name": null,
      "last_name": "Sharma",
      "gender": "male",
      "father_name": "Rohit Sharma",
      "date_of_birth": "2018-04-12",
      "student_mobile": null,
      "parent_mobile": "+919876543210",
      "email": "parent@example.com",
      "address": "12 School Road, Pune",
      "last_school": "Green Valley School",
      "current_class": "Grade 4",
      "admission_for_class": "Grade 5",
      "last_school_percentage": "87.50",
      "admission_for_class_id": 1,
      "status": "PENDING",
      "rejection_reason": "Required admission document is missing.",
      "internal_notes": "Documents reviewed by the admissions office.",
      "created_at": "2026-10-20T10:00:00Z",
      "updated_at": "2026-10-20T10:00:00Z"
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  },
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_records": 1,
    "total_pages": 1
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/inquiries/{inquiry_id}`

Get Inquiry

Get full inquiry details including status history.

**Group:** `inquiries`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `inquiries.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `inquiry_id` | path | Yes | integer | Numeric database ID of the inquiry. Use the `id` from GET /api/v1/inquiries; this is not the human-readable inquiry_code. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Inquiry fetched successfully",
  "data": {
    "id": 1,
    "inquiry_code": "INQ202600007",
    "status_timeline": [],
    "serial_number": 1,
    "first_name": "Aarav",
    "middle_name": null,
    "last_name": "Sharma",
    "gender": "male",
    "father_name": "Rohit Sharma",
    "date_of_birth": "2018-04-12",
    "student_mobile": null,
    "parent_mobile": "+919876543210",
    "email": "parent@example.com",
    "address": "12 School Road, Pune",
    "last_school": "Green Valley School",
    "current_class": "Grade 4",
    "admission_for_class": "Grade 5",
    "last_school_percentage": "87.50",
    "admission_for_class_id": 1,
    "status": "PENDING",
    "rejection_reason": "Required admission document is missing.",
    "internal_notes": "Documents reviewed by the admissions office.",
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/inquiries/{inquiry_id}`

Update Inquiry Admin

Update staff-only fields (class mapping, internal notes).

**Group:** `inquiries`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `inquiries.review`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `inquiry_id` | path | Yes | integer | Numeric database ID of the inquiry. Use the `id` from GET /api/v1/inquiries; this is not the human-readable inquiry_code. |

**Request body**

Required: Yes
- `application/json`: [`AdminInquiryUpdateRequest`](#admininquiryupdaterequest)

**Illustrative JSON request**

```json
{
  "admission_for_class_id": 1,
  "internal_notes": "Documents reviewed by the admissions office."
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Inquiry updated successfully",
  "data": {
    "id": 1,
    "inquiry_code": "INQ202600007",
    "status_timeline": [],
    "serial_number": 1,
    "first_name": "Aarav",
    "middle_name": null,
    "last_name": "Sharma",
    "gender": "male",
    "father_name": "Rohit Sharma",
    "date_of_birth": "2018-04-12",
    "student_mobile": null,
    "parent_mobile": "+919876543210",
    "email": "parent@example.com",
    "address": "12 School Road, Pune",
    "last_school": "Green Valley School",
    "current_class": "Grade 4",
    "admission_for_class": "Grade 5",
    "last_school_percentage": "87.50",
    "admission_for_class_id": 1,
    "status": "PENDING",
    "rejection_reason": "Required admission document is missing.",
    "internal_notes": "Documents reviewed by the admissions office.",
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/inquiries/{inquiry_id}/review/start`

Start Inquiry Review

Move inquiry from PENDING to UNDER_REVIEW.

**Group:** `inquiries`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `inquiries.review`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `inquiry_id` | path | Yes | integer | Numeric database ID of the inquiry. Use the `id` from GET /api/v1/inquiries; this is not the human-readable inquiry_code. |

**Request body**

Required: No
- `application/json`: anyOf: [`InquiryReviewActionRequest`](#inquiryreviewactionrequest), null

**Illustrative JSON request**

```json
{
  "notes": "Applicant will provide the original documents at the office."
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Inquiry review started",
  "data": {
    "id": 1,
    "inquiry_code": "INQ202600007",
    "status_timeline": [],
    "serial_number": 1,
    "first_name": "Aarav",
    "middle_name": null,
    "last_name": "Sharma",
    "gender": "male",
    "father_name": "Rohit Sharma",
    "date_of_birth": "2018-04-12",
    "student_mobile": null,
    "parent_mobile": "+919876543210",
    "email": "parent@example.com",
    "address": "12 School Road, Pune",
    "last_school": "Green Valley School",
    "current_class": "Grade 4",
    "admission_for_class": "Grade 5",
    "last_school_percentage": "87.50",
    "admission_for_class_id": 1,
    "status": "UNDER_REVIEW",
    "rejection_reason": "Required admission document is missing.",
    "internal_notes": "Documents reviewed by the admissions office.",
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/inquiries/{inquiry_id}/review/process`

Mark Inquiry Processing

Move inquiry from UNDER_REVIEW to PROCESSING (eligible).

**Group:** `inquiries`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `inquiries.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `inquiry_id` | path | Yes | integer | Numeric database ID of the inquiry. Use the `id` from GET /api/v1/inquiries; this is not the human-readable inquiry_code. |

**Request body**

Required: No
- `application/json`: anyOf: [`InquiryReviewActionRequest`](#inquiryreviewactionrequest), null

**Illustrative JSON request**

```json
{
  "notes": "Applicant will provide the original documents at the office."
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Inquiry marked as processing",
  "data": {
    "id": 1,
    "inquiry_code": "INQ202600007",
    "status_timeline": [],
    "serial_number": 1,
    "first_name": "Aarav",
    "middle_name": null,
    "last_name": "Sharma",
    "gender": "male",
    "father_name": "Rohit Sharma",
    "date_of_birth": "2018-04-12",
    "student_mobile": null,
    "parent_mobile": "+919876543210",
    "email": "parent@example.com",
    "address": "12 School Road, Pune",
    "last_school": "Green Valley School",
    "current_class": "Grade 4",
    "admission_for_class": "Grade 5",
    "last_school_percentage": "87.50",
    "admission_for_class_id": 1,
    "status": "PENDING",
    "rejection_reason": "Required admission document is missing.",
    "internal_notes": "Documents reviewed by the admissions office.",
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/inquiries/{inquiry_id}/reject`

Reject Inquiry

Reject inquiry with a parent-visible reason; status becomes REJECTED.

**Group:** `inquiries`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `inquiries.reject`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `inquiry_id` | path | Yes | integer | Numeric database ID of the inquiry. Use the `id` from GET /api/v1/inquiries; this is not the human-readable inquiry_code. |

**Request body**

Required: Yes
- `application/json`: [`InquiryRejectRequest`](#inquiryrejectrequest)

**Illustrative JSON request**

```json
{
  "rejection_reason": "Required admission document is missing."
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Inquiry rejected successfully",
  "data": {
    "id": 1,
    "inquiry_code": "INQ202600007",
    "status_timeline": [],
    "serial_number": 1,
    "first_name": "Aarav",
    "middle_name": null,
    "last_name": "Sharma",
    "gender": "male",
    "father_name": "Rohit Sharma",
    "date_of_birth": "2018-04-12",
    "student_mobile": null,
    "parent_mobile": "+919876543210",
    "email": "parent@example.com",
    "address": "12 School Road, Pune",
    "last_school": "Green Valley School",
    "current_class": "Grade 4",
    "admission_for_class": "Grade 5",
    "last_school_percentage": "87.50",
    "admission_for_class_id": 1,
    "status": "PENDING",
    "rejection_reason": "Required admission document is missing.",
    "internal_notes": "Documents reviewed by the admissions office.",
    "created_at": "2026-10-20T10:00:00Z",
    "updated_at": "2026-10-20T10:00:00Z"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/interviews/inquiries/{inquiry_id}/schedule`

Schedule interview for inquiry

Create interview and set inquiry status to INTERVIEW_SCHEDULED.

**Group:** `interviews`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `interviews.schedule`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `inquiry_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `application/json`: [`InterviewCreateRequest`](#interviewcreaterequest)

**Illustrative JSON request**

```json
{
  "schedule_date": "2026-11-05",
  "schedule_time": "10:30",
  "location": "Room 101",
  "mode": "ONLINE",
  "interviewer_teacher_id": 1,
  "remarks": "Please bring the previous report card."
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Interview scheduled successfully",
  "data": {
    "id": 1,
    "inquiry_id": 1,
    "schedule_date": "2026-11-05",
    "schedule_time": "10:30",
    "location": "Room 101",
    "mode": "OFFLINE",
    "interviewer_teacher_id": 1,
    "remarks": "Please bring the previous report card.",
    "result": "SCHEDULED"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/interviews/inquiries/{inquiry_id}`

List Inquiry Interviews

List all interviews for an inquiry.

**Group:** `interviews`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `interviews.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `inquiry_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Interviews fetched successfully",
  "data": {
    "id": 1,
    "inquiry_id": 1,
    "schedule_date": "2026-11-05",
    "schedule_time": "10:30",
    "location": "Room 101",
    "mode": "OFFLINE",
    "interviewer_teacher_id": 1,
    "remarks": "Please bring the previous report card.",
    "result": "SCHEDULED"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/interviews/{interview_id}/result`

Record Interview Result

Record PASSED, FAILED, or ABSENT and update inquiry status.

**Group:** `interviews`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `interviews.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `interview_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `application/json`: [`InterviewResultUpdateRequest`](#interviewresultupdaterequest)

**Illustrative JSON request**

```json
{
  "result": "PASSED",
  "remarks": "Please bring the previous report card."
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Interview result recorded",
  "data": {
    "id": 1,
    "inquiry_id": 1,
    "schedule_date": "2026-11-05",
    "schedule_time": "10:30",
    "location": "Room 101",
    "mode": "OFFLINE",
    "interviewer_teacher_id": 1,
    "remarks": "Please bring the previous report card.",
    "result": "SCHEDULED"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/interviews/{interview_id}`

Get Interview

**Group:** `interviews`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `interviews.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `interview_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Interview fetched successfully",
  "data": {
    "id": 1,
    "inquiry_id": 1,
    "schedule_date": "2026-11-05",
    "schedule_time": "10:30",
    "location": "Room 101",
    "mode": "OFFLINE",
    "interviewer_teacher_id": 1,
    "remarks": "Please bring the previous report card.",
    "result": "SCHEDULED"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/students/me`

Get My Student Profile

**Group:** `students`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires one of these roles: `STUDENT`.

**Parameters:** None.

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Student profile fetched successfully",
  "data": {
    "student_id": 1,
    "admission_id": "EXAMPLE-CODE",
    "first_name": "Aarav",
    "middle_name": null,
    "last_name": "Sharma",
    "father_name": "Rohit Sharma",
    "mother_name": "Example mother name",
    "date_of_birth": "2018-04-12",
    "gender": "male",
    "class_name": "Example class name",
    "section": "A",
    "academic_year": "2026-2027",
    "email": "parent@example.com",
    "phone": "+919876543211",
    "address": "12 School Road, Pune",
    "admission_date": "2026-10-20T10:00:00Z",
    "student_photo_url": "Example student photo url",
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |

### `GET /api/v1/students/me/fees`

Get My Student Fee Details

**Group:** `students`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires one of these roles: `STUDENT`.

**Parameters:** None.

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Student fee schedules fetched successfully",
  "data": {
    "student_id": 1,
    "class_id": 1,
    "academic_year": "2026-2027",
    "admission_fee_structure": {
      "id": 1,
      "academic_year": "2026-2027",
      "class_id": 1,
      "school_class": {
        "id": 1,
        "name": "Grade 5",
        "section": "A",
        "academic_year": "2026-2027"
      },
      "structure_name": "Example structure name",
      "description": "Example description",
      "is_active": true,
      "components": [
        {
          "id": 1,
          "fee_name": "Example fee name",
          "amount": 1.0,
          "is_refundable": true,
          "is_optional": true,
          "description": "Example description",
          "created_at": "2026-10-20T10:00:00Z"
        }
      ],
      "created_at": "2026-10-20T10:00:00Z",
      "updated_at": "2026-10-20T10:00:00Z"
    },
    "monthly_fee_structure": {
      "id": 1,
      "academic_year": "2026-2027",
      "class_id": 1,
      "school_class": {
        "id": 1,
        "name": "Grade 5",
        "section": "A",
        "academic_year": "2026-2027"
      },
      "structure_name": "Example structure name",
      "description": "Example description",
      "is_active": true,
      "components": [
        {
          "id": 1,
          "fee_name": "Example fee name",
          "amount": 1.0,
          "billing_frequency": "MONTHLY",
          "is_optional": true,
          "description": "Example description",
          "created_at": "2026-10-20T10:00:00Z"
        }
      ],
      "created_at": "2026-10-20T10:00:00Z",
      "updated_at": "2026-10-20T10:00:00Z"
    },
    "payment_records_available": false,
    "paid_amount": 1.0,
    "pending_amount": 1.0,
    "upcoming_due_date": "2026-10-20",
    "payment_status": "Example payment status",
    "billing_message": "Example billing message"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |

### `GET /api/v1/students/me/fees/monthly/pdf`

Download My Monthly Fee Pdf

**Group:** `students`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires one of these roles: `STUDENT`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `month` | query | Yes | integer | — |
| `year` | query | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | — |
| `501` | Fee invoices and payment records are not configured. | — |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/students/{student_id}/subjects`

List Student Subjects

**Group:** `students`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `students.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `student_id` | path | Yes | integer | Numeric database ID of the student. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Student class subjects fetched successfully",
  "data": [
    {
      "id": 1,
      "code": "MATH",
      "name": "Mathematics",
      "is_active": true
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/students`

Create Student

**Group:** `students`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `students.create`.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`StudentCreateRequest`](#studentcreaterequest)

**Illustrative JSON request**

```json
{
  "admission_no": "ADM2026001",
  "first_name": "Aarav",
  "last_name": "Sharma",
  "date_of_birth": "2018-04-12",
  "gender": "male",
  "email": "parent@example.com",
  "phone": "+919876543211",
  "current_class_id": 1
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Student created successfully",
  "data": {
    "id": 1,
    "admission_no": "ADM2026001",
    "first_name": "Aarav",
    "last_name": "Sharma",
    "date_of_birth": "2018-04-12",
    "gender": "male",
    "email": "parent@example.com",
    "phone": "+919876543211",
    "current_class_id": 1,
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/students`

List Students

**Group:** `students`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `students.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `status` | query | No | anyOf: string, null | Filter by student status: prospective, active, inactive, graduated, or transferred. |
| `current_class_id` | query | No | anyOf: integer, null; Example: `1` | Filter by current class catalog ID. |
| `search` | query | No | anyOf: string, null | Search by student name or admission number. |
| `page` | query | No | integer | 1-based page number to return. |
| `limit` | query | No | integer | Number of records per page, from 1 to 100. |
| `sort_by` | query | No | string | Field used to sort results; supported fields depend on the endpoint. |
| `sort_order` | query | No | string; Allowed values: `asc, desc` | Sort direction: asc or desc. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Records fetched successfully",
  "data": [
    {
      "id": 1,
      "admission_no": "ADM2026001",
      "first_name": "Aarav",
      "last_name": "Sharma",
      "date_of_birth": "2018-04-12",
      "gender": "male",
      "email": "parent@example.com",
      "phone": "+919876543211",
      "current_class_id": 1,
      "status": "active"
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  },
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_records": 1,
    "total_pages": 1
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/students/{student_id}`

Get Student

**Group:** `students`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `students.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `student_id` | path | Yes | integer | Numeric database ID of the student. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Student fetched successfully",
  "data": {
    "id": 1,
    "admission_no": "ADM2026001",
    "first_name": "Aarav",
    "last_name": "Sharma",
    "date_of_birth": "2018-04-12",
    "gender": "male",
    "email": "parent@example.com",
    "phone": "+919876543211",
    "current_class_id": 1,
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/students/{student_id}`

Update Student

**Group:** `students`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `students.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `student_id` | path | Yes | integer | Numeric database ID of the student. |

**Request body**

Required: Yes
- `application/json`: [`StudentUpdateRequest`](#studentupdaterequest)

**Illustrative JSON request**

```json
{
  "first_name": "Aarav",
  "last_name": "Sharma",
  "date_of_birth": "2018-04-12",
  "gender": "male",
  "email": "parent@example.com",
  "phone": "+919876543211",
  "current_class_id": 1
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Student updated successfully",
  "data": {
    "id": 1,
    "admission_no": "ADM2026001",
    "first_name": "Aarav",
    "last_name": "Sharma",
    "date_of_birth": "2018-04-12",
    "gender": "male",
    "email": "parent@example.com",
    "phone": "+919876543211",
    "current_class_id": 1,
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `DELETE /api/v1/students/{student_id}`

Delete Student

**Group:** `students`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `students.delete`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `student_id` | path | Yes | integer | Numeric database ID of the student. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Student deleted successfully",
  "data": null,
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/students/{student_id}/status`

Update Student Status

**Group:** `students`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `students.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `student_id` | path | Yes | integer | Numeric database ID of the student. |

**Request body**

Required: Yes
- `application/json`: [`StatusUpdateRequest`](#statusupdaterequest)

**Illustrative JSON request**

```json
{
  "status": "active",
  "reason": "Updated student enrollment status."
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Student status updated successfully",
  "data": {
    "id": 1,
    "admission_no": "ADM2026001",
    "first_name": "Aarav",
    "last_name": "Sharma",
    "date_of_birth": "2018-04-12",
    "gender": "male",
    "email": "parent@example.com",
    "phone": "+919876543211",
    "current_class_id": 1,
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/students/{student_id}/class`

Assign Student Class

**Group:** `students`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `students.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `student_id` | path | Yes | integer | Numeric database ID of the student. |

**Request body**

Required: Yes
- `application/json`: [`StudentClassAssignRequest`](#studentclassassignrequest)

**Illustrative JSON request**

```json
{
  "class_id": 1,
  "academic_year": "2026-2027"
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Student class assigned successfully",
  "data": {
    "id": 1,
    "admission_no": "ADM2026001",
    "first_name": "Aarav",
    "last_name": "Sharma",
    "date_of_birth": "2018-04-12",
    "gender": "male",
    "email": "parent@example.com",
    "phone": "+919876543211",
    "current_class_id": 1,
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/subjects`

Create Subject

**Group:** `subjects`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `subjects.create`.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`SubjectCreateRequest`](#subjectcreaterequest)

**Illustrative JSON request**

```json
{
  "code": "MATH",
  "name": "Mathematics"
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Subject created successfully",
  "data": {
    "id": 1,
    "code": "MATH",
    "name": "Mathematics",
    "is_active": true
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/subjects`

List Subjects

**Group:** `subjects`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `subjects.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `active` | query | No | anyOf: boolean, null | Filter by active state. |
| `search` | query | No | anyOf: string, null | Search code or name. |
| `page` | query | No | integer | 1-based page number to return. |
| `limit` | query | No | integer | Number of records per page, from 1 to 100. |
| `sort_by` | query | No | string | Field used to sort results; supported fields depend on the endpoint. |
| `sort_order` | query | No | string; Allowed values: `asc, desc` | Sort direction: asc or desc. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Records fetched successfully",
  "data": [
    {
      "id": 1,
      "code": "MATH",
      "name": "Mathematics",
      "is_active": true
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  },
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_records": 1,
    "total_pages": 1
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/subjects/{subject_id}`

Get Subject

**Group:** `subjects`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `subjects.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `subject_id` | path | Yes | integer | Numeric database ID of the subject. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Subject fetched successfully",
  "data": {
    "id": 1,
    "code": "MATH",
    "name": "Mathematics",
    "is_active": true
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/subjects/{subject_id}`

Update Subject

**Group:** `subjects`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `subjects.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `subject_id` | path | Yes | integer | Numeric database ID of the subject. |

**Request body**

Required: Yes
- `application/json`: [`SubjectUpdateRequest`](#subjectupdaterequest)

**Illustrative JSON request**

```json
{
  "code": "MATH",
  "name": "Mathematics"
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Subject updated successfully",
  "data": {
    "id": 1,
    "code": "MATH",
    "name": "Mathematics",
    "is_active": true
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `DELETE /api/v1/subjects/{subject_id}`

Deactivate Subject

**Group:** `subjects`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `subjects.delete`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `subject_id` | path | Yes | integer | Numeric database ID of the subject. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Subject deactivated successfully",
  "data": {
    "id": 1,
    "code": "MATH",
    "name": "Mathematics",
    "is_active": false
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/subjects/{subject_id}/activate`

Activate Subject

**Group:** `subjects`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `subjects.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `subject_id` | path | Yes | integer | Numeric database ID of the subject. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Subject activated successfully",
  "data": {
    "id": 1,
    "code": "MATH",
    "name": "Mathematics",
    "is_active": true
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/inquiry-admissions`

List Inquiry Admissions

**Group:** `admissions`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `admissions.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `status` | query | No | anyOf: string, null | Filter by admission state: draft, submitted, document_pending, document_verification, approved, or rejected. |
| `academic_year` | query | No | anyOf: string, null; Example: `2026-2027` | Filter by academic year. |
| `page` | query | No | integer | 1-based page number to return. |
| `limit` | query | No | integer | Number of records per page, from 1 to 100. |
| `sort_by` | query | No | string | Field used to sort results; supported fields depend on the endpoint. |
| `sort_order` | query | No | string; Allowed values: `asc, desc` | Sort direction: asc or desc. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Records fetched successfully",
  "data": [
    {
      "id": 1,
      "admission_code": "ADM202600055",
      "inquiry_id": 1,
      "class_id": 1,
      "class_name": "Example class name",
      "section": "A",
      "academic_year": "2026-2027",
      "status": "submitted",
      "permanent_address": "12 School Road, Pune",
      "student_aadhaar_masked": "Example student aadhaar masked",
      "parent_aadhaar_masked": "Example parent aadhaar masked",
      "last_school_marks": 1.0,
      "last_school_percentage": 87.5,
      "last_school_id_or_roll_number": "Example last school id or roll number",
      "temporary_address": "12 School Road, Pune",
      "nationality": "Indian",
      "disability": "Requires wheelchair access",
      "blood_group": "O+",
      "reason_for_school_change": "Family relocation.",
      "rejection_reason": "Required admission document is missing.",
      "notes": "Applicant will provide the original documents at the office.",
      "student_id": 1,
      "documents": []
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  },
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_records": 1,
    "total_pages": 1
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/inquiries/{inquiry_id}/admission`

Create admission from inquiry (after interview pass)

**Group:** `admissions`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `admissions.create`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `inquiry_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `application/json`: [`InquiryAdmissionCreateRequest`](#inquiryadmissioncreaterequest)

**Illustrative JSON request**

```json
{
  "class_id": 1,
  "section": "A",
  "academic_year": "2026-2027",
  "permanent_address": "12 School Road, Pune",
  "student_aadhaar": "Example student aadhaar",
  "parent_aadhaar": "Example parent aadhaar",
  "last_school_marks": 1.0,
  "last_school_percentage": 87.5,
  "last_school_id_or_roll_number": "Example last school id or roll number",
  "temporary_address": "12 School Road, Pune",
  "nationality": "Indian",
  "disability": "Requires wheelchair access",
  "blood_group": "O+",
  "reason_for_school_change": "Family relocation.",
  "notes": "Applicant will provide the original documents at the office."
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Admission created successfully",
  "data": {
    "id": 1,
    "admission_code": "ADM202600055",
    "inquiry_id": 1,
    "class_id": 1,
    "class_name": "Example class name",
    "section": "A",
    "academic_year": "2026-2027",
    "status": "submitted",
    "permanent_address": "12 School Road, Pune",
    "student_aadhaar_masked": "Example student aadhaar masked",
    "parent_aadhaar_masked": "Example parent aadhaar masked",
    "last_school_marks": 1.0,
    "last_school_percentage": 87.5,
    "last_school_id_or_roll_number": "Example last school id or roll number",
    "temporary_address": "12 School Road, Pune",
    "nationality": "Indian",
    "disability": "Requires wheelchair access",
    "blood_group": "O+",
    "reason_for_school_change": "Family relocation.",
    "rejection_reason": "Required admission document is missing.",
    "notes": "Applicant will provide the original documents at the office.",
    "student_id": 1,
    "documents": []
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/inquiry-admissions/{admission_id}`

Get Inquiry Admission

**Group:** `admissions`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `admissions.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `admission_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Admission fetched successfully",
  "data": {
    "id": 1,
    "admission_code": "ADM202600055",
    "inquiry_id": 1,
    "class_id": 1,
    "class_name": "Example class name",
    "section": "A",
    "academic_year": "2026-2027",
    "status": "submitted",
    "permanent_address": "12 School Road, Pune",
    "student_aadhaar_masked": "Example student aadhaar masked",
    "parent_aadhaar_masked": "Example parent aadhaar masked",
    "last_school_marks": 1.0,
    "last_school_percentage": 87.5,
    "last_school_id_or_roll_number": "Example last school id or roll number",
    "temporary_address": "12 School Road, Pune",
    "nationality": "Indian",
    "disability": "Requires wheelchair access",
    "blood_group": "O+",
    "reason_for_school_change": "Family relocation.",
    "rejection_reason": "Required admission document is missing.",
    "notes": "Applicant will provide the original documents at the office.",
    "student_id": 1,
    "documents": []
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/inquiry-admissions/{admission_id}`

Update Inquiry Admission

**Group:** `admissions`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `admissions.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `admission_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `application/json`: [`InquiryAdmissionUpdateRequest`](#inquiryadmissionupdaterequest)

**Illustrative JSON request**

```json
{
  "class_id": 1,
  "section": "A",
  "academic_year": "2026-2027",
  "permanent_address": "12 School Road, Pune",
  "temporary_address": "12 School Road, Pune",
  "nationality": "Indian",
  "disability": "Requires wheelchair access",
  "blood_group": "O+",
  "reason_for_school_change": "Family relocation.",
  "notes": "Applicant will provide the original documents at the office."
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Admission updated successfully",
  "data": {
    "id": 1,
    "admission_code": "ADM202600055",
    "inquiry_id": 1,
    "class_id": 1,
    "class_name": "Example class name",
    "section": "A",
    "academic_year": "2026-2027",
    "status": "submitted",
    "permanent_address": "12 School Road, Pune",
    "student_aadhaar_masked": "Example student aadhaar masked",
    "parent_aadhaar_masked": "Example parent aadhaar masked",
    "last_school_marks": 1.0,
    "last_school_percentage": 87.5,
    "last_school_id_or_roll_number": "Example last school id or roll number",
    "temporary_address": "12 School Road, Pune",
    "nationality": "Indian",
    "disability": "Requires wheelchair access",
    "blood_group": "O+",
    "reason_for_school_change": "Family relocation.",
    "rejection_reason": "Required admission document is missing.",
    "notes": "Applicant will provide the original documents at the office.",
    "student_id": 1,
    "documents": []
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/documents/{document_id}/verify`

Verify Document

**Group:** `admissions`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `admissions.verify_documents`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `document_id` | path | Yes | integer | — |
| `verified` | query | No | boolean | Set true to verify the document or false to reject it. |

**Request body**

Required: No
- `application/json`: anyOf: [`DocumentVerifyRequest`](#documentverifyrequest), null

**Illustrative JSON request**

```json
{
  "rejection_reason": "Required admission document is missing."
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Document verification updated",
  "data": {
    "id": 1,
    "admission_id": 1,
    "document_type": "progress_report",
    "file_name": "progress-report.pdf",
    "verification_status": "PENDING",
    "rejection_reason": "Required admission document is missing.",
    "verified_at": "2026-10-20T10:00:00Z"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/documents/{document_id}/file`

View an uploaded admission document

**Group:** `admissions`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `admissions.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `document_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

The handler does not have a declared response model in OpenAPI; its exact data structure must be checked in the route implementation.

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/documents/required`

List Required Documents

**Group:** `admissions`

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Required documents listed",
  "data": {
    "required": [
      "progress_report",
      "transfer_certificate",
      "migration_certificate",
      "character_certificate",
      "student_aadhar",
      "parent_aadhar"
    ]
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |

### `POST /api/v1/inquiry-admissions/{admission_id}/approve`

Approve Inquiry Admission

**Group:** `admissions`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `admissions.approve`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `admission_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Admission approved for enrollment",
  "data": {
    "id": 1,
    "admission_code": "ADM202600055",
    "inquiry_id": 1,
    "class_id": 1,
    "class_name": "Example class name",
    "section": "A",
    "academic_year": "2026-2027",
    "status": "submitted",
    "permanent_address": "12 School Road, Pune",
    "student_aadhaar_masked": "Example student aadhaar masked",
    "parent_aadhaar_masked": "Example parent aadhaar masked",
    "last_school_marks": 1.0,
    "last_school_percentage": 87.5,
    "last_school_id_or_roll_number": "Example last school id or roll number",
    "temporary_address": "12 School Road, Pune",
    "nationality": "Indian",
    "disability": "Requires wheelchair access",
    "blood_group": "O+",
    "reason_for_school_change": "Family relocation.",
    "rejection_reason": "Required admission document is missing.",
    "notes": "Applicant will provide the original documents at the office.",
    "student_id": 1,
    "documents": []
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/inquiry-admissions/{admission_id}/reject`

Reject Inquiry Admission

**Group:** `admissions`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `admissions.reject`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `admission_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `application/json`: [`RejectionRequest`](#rejectionrequest)

**Illustrative JSON request**

```json
{
  "rejection_reason": "Required admission document is missing."
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Admission rejected",
  "data": {
    "id": 1,
    "admission_code": "ADM202600055",
    "inquiry_id": 1,
    "class_id": 1,
    "class_name": "Example class name",
    "section": "A",
    "academic_year": "2026-2027",
    "status": "submitted",
    "permanent_address": "12 School Road, Pune",
    "student_aadhaar_masked": "Example student aadhaar masked",
    "parent_aadhaar_masked": "Example parent aadhaar masked",
    "last_school_marks": 1.0,
    "last_school_percentage": 87.5,
    "last_school_id_or_roll_number": "Example last school id or roll number",
    "temporary_address": "12 School Road, Pune",
    "nationality": "Indian",
    "disability": "Requires wheelchair access",
    "blood_group": "O+",
    "reason_for_school_change": "Family relocation.",
    "rejection_reason": "Required admission document is missing.",
    "notes": "Applicant will provide the original documents at the office.",
    "student_id": 1,
    "documents": []
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/inquiry-admissions/{admission_id}/enroll`

Enroll student — assigns STU code and roll number

**Group:** `admissions`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `enrollment.create`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `admission_id` | path | Yes | integer | — |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Student enrolled successfully",
  "data": {
    "student_id": 1,
    "student_code": "STU202600001",
    "admission_id": 1,
    "admission_code": "RPS00001",
    "inquiry_code": "INQ202600007",
    "class_id": 1,
    "section": "A",
    "academic_year": "2026-2027",
    "roll_number": 1
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/students/admissions/all`

List Legacy Admissions

**Group:** `admissions`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `admissions.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `status` | query | No | anyOf: string, null | Filter by legacy admission state. |
| `academic_year` | query | No | anyOf: string, null; Example: `2026-2027` | Filter by academic year. |
| `page` | query | No | integer | 1-based page number to return. |
| `limit` | query | No | integer | Number of records per page, from 1 to 100. |
| `sort_by` | query | No | string | Field used to sort results; supported fields depend on the endpoint. |
| `sort_order` | query | No | string; Allowed values: `asc, desc` | Sort direction: asc or desc. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Records fetched successfully",
  "data": [
    {
      "id": 1,
      "student_id": 1,
      "class_id": 1,
      "academic_year": "2026-2027",
      "status": "submitted",
      "rejection_reason": "Required admission document is missing.",
      "notes": "Applicant will provide the original documents at the office."
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  },
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_records": 1,
    "total_pages": 1
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/teachers`

Create Teacher

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.create`.

**Parameters:** None.

**Request body**

Required: Yes
- `application/json`: [`TeacherCreateRequest`](#teachercreaterequest)

**Illustrative JSON request**

```json
{
  "employee_no": "EMP-2026-001",
  "first_name": "Aarav",
  "last_name": "Sharma",
  "email": "parent@example.com",
  "phone": "+919876543211",
  "joining_date": "2026-04-01",
  "user_id": 1
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Teacher created successfully",
  "data": {
    "id": 1,
    "employee_no": "EMP-2026-001",
    "first_name": "Aarav",
    "last_name": "Sharma",
    "email": "parent@example.com",
    "phone": "+919876543211",
    "joining_date": "2026-04-01",
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/teachers`

List Teachers

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `status` | query | No | anyOf: [`TeacherStatus`](#teacherstatus), null | Filter by employment status: active, inactive, or resigned. |
| `search` | query | No | anyOf: string, null | Search by teacher name or employee number. |
| `page` | query | No | integer | 1-based page number to return. |
| `limit` | query | No | integer | Number of records per page, from 1 to 100. |
| `sort_by` | query | No | string | Field used to sort results; supported fields depend on the endpoint. |
| `sort_order` | query | No | string; Allowed values: `asc, desc` | Sort direction: asc or desc. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Records fetched successfully",
  "data": [
    {
      "id": 1,
      "employee_no": "EMP-2026-001",
      "first_name": "Aarav",
      "last_name": "Sharma",
      "email": "parent@example.com",
      "phone": "+919876543211",
      "joining_date": "2026-04-01",
      "status": "active"
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  },
  "pagination": {
    "page": 1,
    "limit": 10,
    "total_records": 1,
    "total_pages": 1
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/teachers/{teacher_id}`

Get Teacher

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `teacher_id` | path | Yes | integer | Numeric database ID of the teacher. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Teacher fetched successfully",
  "data": {
    "id": 1,
    "employee_no": "EMP-2026-001",
    "first_name": "Aarav",
    "last_name": "Sharma",
    "email": "parent@example.com",
    "phone": "+919876543211",
    "joining_date": "2026-04-01",
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `PUT /api/v1/teachers/{teacher_id}`

Update Teacher

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `teacher_id` | path | Yes | integer | Numeric database ID of the teacher. |

**Request body**

Required: Yes
- `application/json`: [`TeacherUpdateRequest`](#teacherupdaterequest)

**Illustrative JSON request**

```json
{
  "first_name": "Aarav",
  "last_name": "Sharma",
  "email": "parent@example.com",
  "phone": "+919876543211",
  "status": "active"
}
```

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Teacher updated successfully",
  "data": {
    "id": 1,
    "employee_no": "EMP-2026-001",
    "first_name": "Aarav",
    "last_name": "Sharma",
    "email": "parent@example.com",
    "phone": "+919876543211",
    "joining_date": "2026-04-01",
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/teachers/{teacher_id}/subject`

Assign Subject

Compatibility assignment for a global teacher/subject link.

Use the class-subjects endpoint for class-specific teaching allocations.

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `teacher_id` | path | Yes | integer | Numeric database ID of the teacher. |

**Request body**

Required: Yes
- `application/json`: [`SubjectAssignRequest`](#subjectassignrequest)

**Illustrative JSON request**

```json
{
  "subject_id": 1
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Subject assigned successfully",
  "data": {
    "subject_id": 1
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/teachers/{teacher_id}/subject`

List Teacher Subjects

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `teacher_id` | path | Yes | integer | Numeric database ID of the teacher. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Subjects fetched successfully",
  "data": [
    {
      "id": 1,
      "code": "MATH",
      "name": "Mathematics"
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/teachers/{teacher_id}/class-subjects`

List Teacher Class Subjects

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `teacher_id` | path | Yes | integer | Numeric database ID of the teacher. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Teacher class-subject assignments fetched successfully",
  "data": [
    {
      "class_id": 1,
      "subject_id": 1,
      "class_name": "Grade 5",
      "subject_name": "Mathematics"
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/teachers/{teacher_id}/class-subjects`

Assign Teacher Class Subject

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `teacher_id` | path | Yes | integer | Numeric database ID of the teacher. |

**Request body**

Required: Yes
- `application/json`: [`TeacherClassSubjectAssignRequest`](#teacherclasssubjectassignrequest)

**Illustrative JSON request**

```json
{
  "class_id": 1,
  "subject_id": 1
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Teacher assigned to class subject successfully",
  "data": {
    "teacher_id": 1,
    "class_id": 1,
    "subject_id": 1
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/teachers/{teacher_id}/academic-readiness`

Get Teacher Academic Readiness

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `teacher_id` | path | Yes | integer | Numeric database ID of the teacher. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Teacher academic readiness fetched successfully",
  "data": {
    "teacher_id": 1,
    "ready": true,
    "assignments": [
      {
        "class_id": 1,
        "subject_id": 1,
        "class_name": "Grade 5",
        "subject_name": "Mathematics"
      }
    ],
    "issues": []
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `DELETE /api/v1/teachers/{teacher_id}/class-subjects/{class_id}/{subject_id}`

Remove Teacher Class Subject

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `teacher_id` | path | Yes | integer | Numeric database ID of the teacher. |
| `class_id` | path | Yes | integer | Numeric database ID of the class. |
| `subject_id` | path | Yes | integer | Numeric database ID of the subject. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Teacher class-subject assignment removed successfully",
  "data": null,
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/teachers/{teacher_id}/class`

Assign Class

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `teacher_id` | path | Yes | integer | Numeric database ID of the teacher. |

**Request body**

Required: Yes
- `application/json`: [`ClassAssignRequest`](#classassignrequest)

**Illustrative JSON request**

```json
{
  "class_id": 1
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Class assigned successfully",
  "data": {
    "class_id": 1
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/teachers/{teacher_id}/class`

List Teacher Classes

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `teacher_id` | path | Yes | integer | Numeric database ID of the teacher. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Classes fetched successfully",
  "data": [
    {
      "id": 1,
      "name": "Grade 5",
      "section": "A",
      "academic_year": "2026-2027"
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/teachers/{teacher_id}/attendance`

Record Attendance

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `teacher_id` | path | Yes | integer | Numeric database ID of the teacher. |

**Request body**

Required: Yes
- `application/json`: [`AttendanceCreateRequest`](#attendancecreaterequest)

**Illustrative JSON request**

```json
{
  "attendance_date": "2026-10-19",
  "status": "present",
  "remarks": "Please bring the previous report card."
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Attendance recorded successfully",
  "data": {
    "id": 1,
    "teacher_id": 1,
    "attendance_date": "2026-10-19",
    "status": "present",
    "remarks": "Please bring the previous report card."
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /api/v1/teachers/{teacher_id}/salary`

Get Teacher Salary

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.salary.read`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `teacher_id` | path | Yes | integer | Numeric database ID of the teacher. |

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Salary fetched successfully",
  "data": {
    "id": 1,
    "teacher_id": 1,
    "base_salary": 50000.0,
    "allowance": 1.0,
    "deduction": 1.0,
    "effective_from": "2026-04-01",
    "status": "active"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `POST /api/v1/teachers/{teacher_id}/salary/payments`

Create Salary Payment

**Group:** `teachers`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `teachers.salary.pay`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `teacher_id` | path | Yes | integer | Numeric database ID of the teacher. |

**Request body**

Required: Yes
- `application/json`: [`SalaryPaymentCreateRequest`](#salarypaymentcreaterequest)

**Illustrative JSON request**

```json
{
  "payment_month": "2026-10",
  "gross_amount": 50000.0,
  "deduction_amount": 2500.0,
  "net_amount": "47500.00",
  "status": "pending",
  "paid_at": "2026-10-20T10:00:00Z"
}
```

**Illustrative success response**

HTTP `201`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Salary payment recorded successfully",
  "data": {
    "id": 1,
    "teacher_id": 1,
    "salary_id": 1,
    "payment_month": "2026-10",
    "gross_amount": 50000.0,
    "deduction_amount": 2500.0,
    "net_amount": "47500.00",
    "status": "paid",
    "paid_at": "2026-10-20T10:00:00Z"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `201` | Successful Response | `application/json`: object |
| `422` | Validation Error | Standard API error envelope; see [HTTP 422 example](#http-422-validation-error). The runtime handler replaces FastAPI's default validation-error body. |

**Validation failure example:** See [HTTP 422 error example](#http-422-validation-error). The exact error field/message depends on which path, query, header, form, or body rule failed.

### `GET /ready`

Readiness Check

Readiness probe; returns 503 when the database cannot execute SELECT 1.

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Records fetched successfully",
  "data": {
    "status": "ready",
    "database": true
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |

### `GET /health`

Readiness Check

Readiness probe; returns 503 when the database cannot execute SELECT 1.

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Records fetched successfully",
  "data": {
    "status": "ready",
    "database": true
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |

### `GET /live`

Liveness Check

Liveness probe; checks only that the API process can serve requests.

**OpenAPI authentication:** Not specified by OpenAPI

**Authorization requirement:** Public route; no bearer token dependency declared.

**Parameters:** None.

**Request body:** Not used by this endpoint.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Service alive",
  "data": {
    "status": "alive"
  },
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

**Responses**

| HTTP status | Description | Response schema |
|---:|---|---|
| `200` | Successful Response | `application/json`: object |

## Common runtime error examples

The exception handlers return the shared API error envelope. OpenAPI declares request validation status `422`, but it does not list every application exception status for every operation. The additional examples below describe runtime formats; whether a status applies depends on that route's validation, authentication, resource, and business rules.

### HTTP 422 Validation error

Invalid request data and business-rule violations both use HTTP 422; the `errors[].code` distinguishes ordinary input validation from a business rule.

```json
{
  "success": false,
  "message": "Validation failed",
  "data": null,
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "field": "body.email",
      "message": "Invalid email address"
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

### HTTP 401 Authentication required

```json
{
  "success": false,
  "message": "Invalid credentials or token.",
  "data": null,
  "errors": [
    {
      "code": "AUTH_INVALID_CREDENTIALS",
      "message": "Invalid credentials or token."
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

### HTTP 403 Permission denied

```json
{
  "success": false,
  "message": "The user lacks route permission.",
  "data": null,
  "errors": [
    {
      "code": "AUTH_FORBIDDEN",
      "message": "The user lacks route permission."
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

### HTTP 404 Resource not found

```json
{
  "success": false,
  "message": "The requested record does not exist.",
  "data": null,
  "errors": [
    {
      "code": "RESOURCE_NOT_FOUND",
      "message": "The requested record does not exist."
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

### HTTP 409 Resource conflict

```json
{
  "success": false,
  "message": "A uniqueness or database constraint conflict occurred.",
  "data": null,
  "errors": [
    {
      "code": "RESOURCE_CONFLICT",
      "message": "A uniqueness or database constraint conflict occurred."
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

### HTTP 500 Internal server error

```json
{
  "success": false,
  "message": "An unexpected server error occurred.",
  "data": null,
  "errors": [
    {
      "code": "INTERNAL_SERVER_ERROR",
      "message": "An unexpected server error occurred."
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

### HTTP 503 Database unavailable

```json
{
  "success": false,
  "message": "Service unavailable",
  "data": null,
  "errors": [
    {
      "code": "DATABASE_UNAVAILABLE",
      "message": "Database connection is unavailable"
    }
  ],
  "meta": {
    "request_id": "example-request-id",
    "timestamp": "2026-10-20T10:00:00Z"
  }
}
```

## Schemas

Schema links above lead to these definitions. Required fields, types, constraints, enum values, descriptions, and available examples are rendered from the OpenAPI components.

### `AdminInquiryUpdateRequest`

Staff-only field updates (including internal notes and class mapping).

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `admission_for_class_id` | anyOf: integer, null | No | — | Catalog class ID to associate with this inquiry.; Example: `1` |
| `internal_notes` | anyOf: string, null | No | — | Staff-only notes; not visible in parent status responses. |

### `AdmissionFeeComponentCreate`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `fee_name` | string | Yes | Min length: `1`; Max length: `100` | Unique charge name. |
| `amount` | anyOf: number, string | Yes | — | Non-negative amount with a maximum of two decimal places. |
| `is_refundable` | boolean | No | Default: `False` | Whether this charge is refundable. |
| `is_optional` | boolean | No | Default: `False` | Whether families may opt out. |
| `description` | anyOf: string, null | No | — | — |

### `AdmissionFeeComponentUpdate`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `id` | anyOf: integer, null | No | — | Existing component ID; omit to add a component. |
| `fee_name` | anyOf: string, null | No | — | — |
| `amount` | anyOf: number, string, null | No | — | — |
| `is_refundable` | anyOf: boolean, null | No | — | — |
| `is_optional` | anyOf: boolean, null | No | — | — |
| `description` | anyOf: string, null | No | — | — |

### `AdmissionFeeStructureCreate`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `academic_year` | string | Yes | Min length: `4`; Max length: `20` | —; Example: `2026-2027` |
| `class_id` | integer | Yes | — | Existing class in the selected academic year. |
| `structure_name` | string | Yes | Min length: `1`; Max length: `100` | — |
| `description` | anyOf: string, null | No | — | — |
| `is_active` | boolean | No | Default: `True` | — |
| `components` | array of [`AdmissionFeeComponentCreate`](#admissionfeecomponentcreate) | Yes | Min items: `1` | — |

### `AdmissionFeeStructureUpdate`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `academic_year` | anyOf: string, null | No | — | — |
| `class_id` | anyOf: integer, null | No | — | — |
| `structure_name` | anyOf: string, null | No | — | — |
| `description` | anyOf: string, null | No | — | — |
| `is_active` | anyOf: boolean, null | No | — | — |
| `components` | anyOf: array of [`AdmissionFeeComponentUpdate`](#admissionfeecomponentupdate), null | No | — | — |

### `AssessmentCreateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `name` | string | Yes | Min length: `1`; Max length: `200` | — |
| `assessment_type` | string | Yes | Allowed values: `unit_test, periodic_test, mid_term, final_exam, assignment, quiz, practical, oral` | — |
| `class_id` | integer | Yes | — | — |
| `subject_id` | integer | Yes | — | — |
| `teacher_id` | anyOf: integer, null | No | — | — |
| `assessment_date` | string (date) | Yes | — | — |
| `max_score` | anyOf: number, string | Yes | — | — |

### `AssessmentResultRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `score` | anyOf: number, string, null | No | — | — |
| `result_status` | string | No | Allowed values: `present, absent`; Default: `present` | — |
| `remarks` | anyOf: string, null | No | — | — |

### `AssessmentUpdateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `name` | anyOf: string, null | No | — | — |
| `assessment_type` | anyOf: string, null | No | — | — |
| `assessment_date` | anyOf: string (date), null | No | — | — |
| `max_score` | anyOf: number, string, null | No | — | — |

### `AssignmentCreateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `title` | string | Yes | Min length: `1`; Max length: `200` | — |
| `details` | string | Yes | Min length: `1`; Max length: `10000` | — |
| `class_id` | integer | Yes | — | — |
| `subject_id` | integer | Yes | — | — |
| `teacher_id` | anyOf: integer, null | No | — | — |
| `assigned_date` | anyOf: string (date), null | No | — | — |
| `due_date` | string (date) | Yes | — | — |

### `AssignmentUpdateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `title` | anyOf: string, null | No | — | — |
| `details` | anyOf: string, null | No | — | — |
| `due_date` | anyOf: string (date), null | No | — | — |

### `AttendanceCreateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `attendance_date` | string (date) | Yes | — | Date for this attendance record.; Example: `2026-10-19` |
| `status` | [`AttendanceStatus`](#attendancestatus) | Yes | — | Attendance state: present, absent, leave, or half_day. |
| `remarks` | anyOf: string, null | No | — | Optional attendance note. |

### `AttendanceStatus`

**Allowed values:** `present`, `absent`, `leave`, `half_day`

### `BillingFrequency`

Frequency used to bill a recurring fee component.

**Allowed values:** `MONTHLY`, `QUARTERLY`, `ANNUALLY`, `ONE_TIME`

### `Body_submit_admission_api_v1_public_student_admission_post`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `inquiry_code` | string | Yes | Min length: `5`; Max length: `20` | Inquiry tracking code returned when the inquiry was submitted.; Example: `INQ202600007` |
| `email` | string (email) | Yes | — | Email address supplied with the original inquiry. |
| `parent_mobile` | string | Yes | Min length: `5`; Max length: `30` | Parent/guardian mobile number supplied with the original inquiry. |
| `class_id` | integer | Yes | — | Catalog ID of the class requested for admission.; Example: `1` |
| `academic_year` | string | Yes | Min length: `4`; Max length: `20` | Academic year for admission.; Example: `2026-2027` |
| `student_aadhaar` | string | No | Default: `` | 12-digit student Aadhaar number. |
| `parent_aadhaar` | string | No | Default: `` | 12-digit parent/guardian Aadhaar number. |
| `last_school_marks` | string | No | Default: `` | Marks obtained at the previous school. |
| `last_school_percentage` | string | No | Default: `` | Percentage obtained at the previous school. |
| `last_school_id_or_roll_number` | string | No | Default: `` | Previous-school student ID or roll number. |
| `section` | anyOf: string, null | No | — | Optional section within the selected class. |
| `permanent_address` | anyOf: string, null | No | — | Optional permanent residential address. |

### `Body_upload_assignment_attachment_api_v1_assignments__assignment_id__attachments_post`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `file` | string | Yes | — | PDF, JPG, JPEG, or PNG attachment. |

### `Body_upload_public_admission_document_api_v1_public_student_admission_documents_post`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `inquiry_code` | string | Yes | Min length: `5`; Max length: `20` | — |
| `email` | string (email) | Yes | — | — |
| `parent_mobile` | string | Yes | Min length: `5`; Max length: `30` | — |
| `document_type` | string | Yes | — | — |
| `file` | string | Yes | — | — |

### `ChangePasswordRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `current_password` | string | Yes | — | Current account password. |
| `new_password` | string | Yes | Min length: `8` | New password; must meet the configured password policy. |

### `ClassAssignRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `class_id` | integer | Yes | — | ID of the class to assign.; Example: `1` |

### `ClassCreateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `name` | string | Yes | Min length: `1`; Max length: `100` | Class or grade name. |
| `section` | anyOf: string, null | No | — | Optional section identifier. |
| `academic_year` | string | Yes | Min length: `4`; Max length: `20` | Academic year for this class.; Example: `2026-2027` |
| `capacity` | integer | Yes | — | Maximum number of students. |

### `ClassStatus`

Whether a school class record is open for admissions.

**Allowed values:** `active`, `inactive`

### `ClassSubjectAssignRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `subject_id` | integer | Yes | — | Existing active subject catalog ID. |

### `ClassTeacherAssignRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `teacher_id` | integer | Yes | — | Existing active teacher ID. |

### `ClassUpdateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `name` | anyOf: string, null | No | — | Updated class or grade name. |
| `section` | anyOf: string, null | No | — | Updated section identifier. |
| `academic_year` | anyOf: string, null | No | — | Updated academic year.; Example: `2026-2027` |
| `capacity` | anyOf: integer, null | No | — | Updated maximum student count. |
| `status` | anyOf: [`ClassStatus`](#classstatus), null | No | — | Class state: active or inactive. |

### `DashboardSummaryEnvelope`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `success` | boolean | Yes | — | — |
| `message` | string | Yes | — | — |
| `data` | [`DashboardSummaryResponse`](#dashboardsummaryresponse) | Yes | — | — |
| `meta` | [`ResponseMeta`](#responsemeta) | Yes | — | — |

### `DashboardSummaryResponse`

Permission-filtered live dashboard metrics; null fields are not authorized.

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `school_timezone` | string | Yes | — | IANA timezone used for interview scheduling. |
| `student_count` | anyOf: integer, null | No | — | Visible student count. |
| `teacher_count` | anyOf: integer, null | No | — | Teacher count. |
| `class_count` | anyOf: integer, null | No | — | Non-deleted class count. |
| `subject_count` | anyOf: integer, null | No | — | Subject catalog count. |
| `inquiry_count` | anyOf: integer, null | No | — | Inquiry count. |
| `pending_admission_count` | anyOf: integer, null | No | — | Applications in draft, submitted, document_pending, or document_verification. |
| `admissions_by_status` | anyOf: object, null | No | — | Inquiry-linked admission application counts grouped by workflow status. |
| `upcoming_interview_count` | anyOf: integer, null | No | — | Scheduled interviews from the current school-local time onward. |
| `upcoming_interviews` | anyOf: array of [`UpcomingInterviewSummaryItem`](#upcominginterviewsummaryitem), null | No | — | Up to five upcoming interviews; included only with inquiries.read. |

### `DocumentVerifyRequest`

Staff verification of a single document.

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `rejection_reason` | anyOf: string, null | No | — | Reason for rejecting the document; required when verification status is set to REJECTED. |

### `EventCreateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `title` | string | Yes | Min length: `1`; Max length: `200` | — |
| `description` | string | Yes | Min length: `1`; Max length: `10000` | — |
| `starts_at` | string (date-time) | Yes | — | — |
| `ends_at` | string (date-time) | Yes | — | — |
| `venue` | anyOf: string, null | No | — | — |
| `audience` | string | No | Allowed values: `public, students, parents, all`; Default: `all` | — |

### `EventReviewRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `status` | string | Yes | Allowed values: `published, rejected` | — |
| `rejection_reason` | anyOf: string, null | No | — | — |

### `EventUpdateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `title` | anyOf: string, null | No | — | — |
| `description` | anyOf: string, null | No | — | — |
| `starts_at` | anyOf: string (date-time), null | No | — | — |
| `ends_at` | anyOf: string (date-time), null | No | — | — |
| `venue` | anyOf: string, null | No | — | — |
| `audience` | anyOf: string, null | No | — | — |

### `FeeStructureStatusUpdate`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `is_active` | boolean | Yes | — | Whether the fee structure is active. |

### `Gender`

Student gender values accepted on public inquiry forms.

**Allowed values:** `male`, `female`, `other`

### `HTTPValidationError`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `detail` | array of [`ValidationError`](#validationerror) | No | — | — |

### `InquiryAdmissionCreateRequest`

Submit admission application after interview pass (staff or verified parent).

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `class_id` | integer | Yes | — | Target class catalog ID.; Example: `1` |
| `section` | anyOf: string, null | No | — | Requested class section. |
| `academic_year` | string | Yes | Min length: `4`; Max length: `20` | Academic year for admission.; Example: `2026-2027` |
| `permanent_address` | anyOf: string, null | No | — | Applicant's permanent residential address. |
| `student_aadhaar` | anyOf: string, null | No | — | Student Aadhaar number; encrypted at rest and never returned by the API. |
| `parent_aadhaar` | anyOf: string, null | No | — | Parent/guardian Aadhaar number; encrypted at rest and never returned by the API. |
| `last_school_marks` | anyOf: number, string, null | No | — | Marks obtained at the previous school. |
| `last_school_percentage` | anyOf: number, string, null | No | — | Previous-school percentage, from 0 to 100. |
| `last_school_id_or_roll_number` | anyOf: string, null | No | — | Student ID or roll number from the previous school. |
| `temporary_address` | anyOf: string, null | No | — | Applicant's current address if different. |
| `nationality` | anyOf: string, null | No | — | Applicant's nationality. |
| `disability` | anyOf: string, null | No | — | Disability information relevant to school support, if any.; Example: `Requires wheelchair access` |
| `blood_group` | anyOf: string, null | No | — | Applicant's blood group, if known.; Example: `O+` |
| `reason_for_school_change` | anyOf: string, null | No | — | Reason for changing schools. |
| `notes` | anyOf: string, null | No | — | Additional admission application notes. |

### `InquiryAdmissionUpdateRequest`

Update draft/submitted admission details.

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `class_id` | anyOf: integer, null | No | — | Updated target class catalog ID.; Example: `1` |
| `section` | anyOf: string, null | No | — | Updated requested class section. |
| `academic_year` | anyOf: string, null | No | — | Updated academic year.; Example: `2026-2027` |
| `permanent_address` | anyOf: string, null | No | — | Updated permanent residential address. |
| `temporary_address` | anyOf: string, null | No | — | Updated current address, if different. |
| `nationality` | anyOf: string, null | No | — | Updated nationality. |
| `disability` | anyOf: string, null | No | — | Updated disability/support information.; Example: `Requires wheelchair access` |
| `blood_group` | anyOf: string, null | No | — | Updated blood group, if known.; Example: `O+` |
| `reason_for_school_change` | anyOf: string, null | No | — | Updated reason for changing schools. |
| `notes` | anyOf: string, null | No | — | Updated additional application notes. |

### `InquiryRejectRequest`

Reject an inquiry with a mandatory parent-visible reason.

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `rejection_reason` | string | Yes | Min length: `3` | Reason for rejection; shown to the parent. |

### `InquiryReviewActionRequest`

Body for admin review transition endpoints.

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `notes` | anyOf: string, null | No | — | Optional staff note recorded with the status transition. |

### `InterviewCreateRequest`

Staff request to schedule an interview for an inquiry.

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `schedule_date` | string (date) | Yes | — | Date of the interview.; Example: `2026-11-05` |
| `schedule_time` | string (time) | Yes | — | Start time in 24-hour HH:MM format.; Example: `10:30` |
| `location` | string | Yes | Min length: `1`; Max length: `255` | Room, address, or meeting location. |
| `mode` | [`InterviewMode`](#interviewmode) | No | Default: `OFFLINE` | Interview mode: ONLINE or OFFLINE. |
| `interviewer_teacher_id` | anyOf: integer, null | No | — | Optional ID of the assigned interviewer. |
| `remarks` | anyOf: string, null | No | — | Optional scheduling notes. |

### `InterviewMode`

How the interview or test is conducted.

**Allowed values:** `ONLINE`, `OFFLINE`

### `InterviewResultUpdate`

Allowed values when staff records interview outcome.

**Allowed values:** `PASSED`, `FAILED`, `ABSENT`

### `InterviewResultUpdateRequest`

Record pass, fail, or absent for a scheduled interview.

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `result` | [`InterviewResultUpdate`](#interviewresultupdate) | Yes | — | Interview outcome: PASSED, FAILED, or ABSENT. |
| `remarks` | anyOf: string, null | No | — | Optional notes about the outcome. |

### `LoginRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `email` | string | Yes | — | Email address registered to the account. |
| `password` | string | Yes | — | Account password. |
| `portal` | anyOf: string, null | No | — | Optional portal role required for this sign-in. |

### `LogoutRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `refresh_token` | string | Yes | — | Refresh token to revoke. |

### `MonthlyFeeComponentCreate`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `fee_name` | string | Yes | Min length: `1`; Max length: `100` | Unique charge name. |
| `amount` | anyOf: number, string | Yes | — | Non-negative amount with a maximum of two decimal places. |
| `billing_frequency` | [`BillingFrequency`](#billingfrequency) | Yes | — | — |
| `is_optional` | boolean | No | Default: `False` | Whether families may opt out. |
| `description` | anyOf: string, null | No | — | — |

### `MonthlyFeeComponentUpdate`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `id` | anyOf: integer, null | No | — | Existing component ID; omit to add a component. |
| `fee_name` | anyOf: string, null | No | — | — |
| `amount` | anyOf: number, string, null | No | — | — |
| `billing_frequency` | anyOf: [`BillingFrequency`](#billingfrequency), null | No | — | — |
| `is_optional` | anyOf: boolean, null | No | — | — |
| `description` | anyOf: string, null | No | — | — |

### `MonthlyFeeStructureCreate`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `academic_year` | string | Yes | Min length: `4`; Max length: `20` | —; Example: `2026-2027` |
| `class_id` | integer | Yes | — | Existing class in the selected academic year. |
| `structure_name` | string | Yes | Min length: `1`; Max length: `100` | — |
| `description` | anyOf: string, null | No | — | — |
| `is_active` | boolean | No | Default: `True` | — |
| `components` | array of [`MonthlyFeeComponentCreate`](#monthlyfeecomponentcreate) | Yes | Min items: `1` | — |

### `MonthlyFeeStructureUpdate`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `academic_year` | anyOf: string, null | No | — | — |
| `class_id` | anyOf: integer, null | No | — | — |
| `structure_name` | anyOf: string, null | No | — | — |
| `description` | anyOf: string, null | No | — | — |
| `is_active` | anyOf: boolean, null | No | — | — |
| `components` | anyOf: array of [`MonthlyFeeComponentUpdate`](#monthlyfeecomponentupdate), null | No | — | — |

### `PaymentStatus`

**Allowed values:** `pending`, `paid`, `failed`

### `PublicInquiryCreateRequest`

Request body for POST /api/v1/public/student/inquiry.

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `first_name` | string | Yes | Min length: `1`; Max length: `100` | Applicant student's given name. |
| `middle_name` | anyOf: string, null | No | — | Optional middle name. |
| `last_name` | string | Yes | Min length: `1`; Max length: `100` | Applicant student's family name. |
| `gender` | [`Gender`](#gender) | Yes | — | Student gender: male, female, or other. |
| `father_name` | string | Yes | Min length: `1`; Max length: `200` | Father's or legal guardian's full name. |
| `dob` | string (date) | Yes | — | Student date of birth (YYYY-MM-DD); cannot be in the future.; Example: `2018-04-12` |
| `student_mobile` | anyOf: string, null | No | — | Optional student contact number. |
| `parent_mobile` | string | Yes | Min length: `5`; Max length: `30` | Parent or guardian phone; also used to verify status lookups. |
| `email` | string (email) | Yes | — | Parent or guardian email; also used to verify status lookups. |
| `address` | string | Yes | Min length: `5` | Applicant's residential address. |
| `last_school` | string | Yes | Min length: `1`; Max length: `255` | Name of the school most recently attended. |
| `current_class` | string | Yes | Min length: `1`; Max length: `100` | Class or grade currently attended. |
| `admission_for_class` | string | Yes | Min length: `1`; Max length: `100` | Class or grade requested for admission. |
| `last_school_percentage` | anyOf: number, string, null | No | — | Most recent school percentage, from 0 to 100.; Example: `87.50` |
| `admission_for_class_id` | anyOf: integer, null | No | — | Optional catalog class ID when known; must identify an active class.; Example: `1` |

### `PublicInquiryUpdateRequest`

Request body for PUT /api/v1/public/student/inquiry/update.

Parent must prove ownership via inquiry_code + email + parent_mobile.

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `inquiry_code` | string | Yes | Min length: `5`; Max length: `20` | Inquiry tracking code returned at submission.; Example: `INQ202600007` |
| `email` | string (email) | Yes | — | Email submitted with this inquiry, used to verify ownership. |
| `parent_mobile` | string | Yes | Min length: `5`; Max length: `30` | Parent/guardian mobile submitted with this inquiry, used to verify ownership. |
| `first_name` | anyOf: string, null | No | — | Updated student given name. |
| `middle_name` | anyOf: string, null | No | — | Updated student middle name. |
| `last_name` | anyOf: string, null | No | — | Updated student family name. |
| `gender` | anyOf: [`Gender`](#gender), null | No | — | Updated gender: male, female, or other. |
| `father_name` | anyOf: string, null | No | — | Updated father or legal guardian name. |
| `dob` | anyOf: string (date), null | No | — | Updated date of birth (YYYY-MM-DD).; Example: `2018-04-12` |
| `student_mobile` | anyOf: string, null | No | — | Updated student contact number. |
| `address` | anyOf: string, null | No | — | Updated residential address. |
| `last_school` | anyOf: string, null | No | — | Updated last school name. |
| `current_class` | anyOf: string, null | No | — | Updated current class or grade. |
| `admission_for_class` | anyOf: string, null | No | — | Updated requested class or grade. |
| `last_school_percentage` | anyOf: number, string, null | No | — | Updated last-school percentage, from 0 to 100.; Example: `87.50` |

### `RefreshTokenRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `refresh_token` | string | Yes | — | Refresh token returned by login. |

### `RejectionRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `rejection_reason` | string | Yes | Min length: `1` | Explanation shown for the rejection. |

### `ResponseMeta`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `request_id` | string | Yes | — | — |
| `timestamp` | string | Yes | — | — |

### `SalaryPaymentCreateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `payment_month` | string | Yes | Pattern: `^\d{4}-\d{2}$` | Salary month in YYYY-MM format.; Example: `2026-10` |
| `gross_amount` | anyOf: number, string | Yes | — | Gross salary amount before deductions. |
| `deduction_amount` | anyOf: number, string | No | Default: `0` | Total deductions; cannot exceed gross_amount. |
| `net_amount` | anyOf: number, string | Yes | — | Take-home amount; must equal gross_amount minus deduction_amount.; Example: `47500.00` |
| `status` | [`PaymentStatus`](#paymentstatus) | No | Default: `paid` | Payment state: pending, paid, or failed. |
| `paid_at` | anyOf: string (date-time), null | No | — | Payment completion timestamp, if paid. |

### `StatusUpdateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `status` | string | Yes | — | New lifecycle or workflow status. |
| `reason` | anyOf: string, null | No | — | Optional explanation for the status change. |

### `StudentClassAssignRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `class_id` | integer | Yes | — | ID of the class to assign.; Example: `1` |
| `academic_year` | string | Yes | Min length: `4`; Max length: `20` | Academic year for the assignment.; Example: `2026-2027` |

### `StudentCreateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `admission_no` | anyOf: string, null | No | — | Optional school-issued admission number.; Example: `ADM2026001` |
| `first_name` | string | Yes | Min length: `1`; Max length: `100` | Student's given name. |
| `last_name` | string | Yes | Min length: `1`; Max length: `100` | Student's family name. |
| `date_of_birth` | string (date) | Yes | — | Student date of birth in YYYY-MM-DD format.; Example: `2018-04-12` |
| `gender` | string | Yes | Min length: `1`; Max length: `20` | Gender value recorded for the student (male, female, or other). |
| `email` | anyOf: string (email), null | No | — | Optional student or guardian email address. |
| `phone` | anyOf: string, null | No | — | Optional student or guardian phone number. |
| `current_class_id` | anyOf: integer, null | No | — | Optional ID of the student's current class.; Example: `1` |

### `StudentPortalLoginRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `student_id` | string | Yes | Min length: `1`; Max length: `50` | — |
| `password` | string | Yes | Min length: `1`; Max length: `128` | — |

### `StudentPortalRegistrationRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `admission_id` | string | Yes | Min length: `1`; Max length: `50` | — |
| `email` | string | Yes | — | — |
| `password` | string | Yes | Min length: `8`; Max length: `128` | — |
| `confirm_password` | string | Yes | Min length: `8`; Max length: `128` | — |

### `StudentUpdateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `first_name` | anyOf: string, null | No | — | Updated given name. |
| `last_name` | anyOf: string, null | No | — | Updated family name. |
| `date_of_birth` | anyOf: string (date), null | No | — | Updated date of birth (YYYY-MM-DD).; Example: `2018-04-12` |
| `gender` | anyOf: string, null | No | — | Updated gender value (male, female, or other). |
| `email` | anyOf: string (email), null | No | — | Updated student or guardian email. |
| `phone` | anyOf: string, null | No | — | Updated contact phone number. |
| `current_class_id` | anyOf: integer, null | No | — | Updated current class ID.; Example: `1` |

### `SubjectAssignRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `subject_id` | integer | Yes | — | ID of the subject to assign. |

### `SubjectCreateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `code` | string | Yes | Min length: `1`; Max length: `50` | Unique subject code.; Example: `MATH` |
| `name` | string | Yes | Min length: `1`; Max length: `100` | Subject display name.; Example: `Mathematics` |

### `SubjectUpdateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `code` | anyOf: string, null | No | — | Updated unique subject code.; Example: `MATH` |
| `name` | anyOf: string, null | No | — | Updated subject display name.; Example: `Mathematics` |

### `TeacherClassSubjectAssignRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `class_id` | integer | Yes | — | Class offering this subject. |
| `subject_id` | integer | Yes | — | Subject already offered to the class. |

### `TeacherCreateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `employee_no` | string | Yes | Min length: `1`; Max length: `50` | Unique employee number.; Example: `EMP-2026-001` |
| `first_name` | string | Yes | Min length: `1`; Max length: `100` | Teacher's given name. |
| `last_name` | string | Yes | Min length: `1`; Max length: `100` | Teacher's family name. |
| `email` | string (email) | Yes | — | Teacher's work email address. |
| `phone` | string | Yes | Min length: `5`; Max length: `30` | Teacher's contact phone number. |
| `joining_date` | string (date) | Yes | — | Employment start date (YYYY-MM-DD).; Example: `2026-04-01` |
| `user_id` | anyOf: integer, null | No | — | Optional existing platform user ID to link. |

### `TeacherStatus`

**Allowed values:** `active`, `inactive`, `resigned`

### `TeacherUpdateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `first_name` | anyOf: string, null | No | — | Updated given name. |
| `last_name` | anyOf: string, null | No | — | Updated family name. |
| `email` | anyOf: string (email), null | No | — | Updated work email address. |
| `phone` | anyOf: string, null | No | — | Updated contact phone number. |
| `status` | anyOf: [`TeacherStatus`](#teacherstatus), null | No | — | Employment status: active, inactive, or resigned. |

### `TimetableCreateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `class_id` | integer | Yes | — | — |
| `subject_id` | integer | Yes | — | — |
| `teacher_id` | anyOf: integer, null | No | — | — |
| `day_of_week` | integer | Yes | Minimum: `0.0`; Maximum: `6.0` | — |
| `start_time` | string (time) | Yes | — | — |
| `end_time` | string (time) | Yes | — | — |
| `room` | anyOf: string, null | No | — | — |
| `academic_year` | string | Yes | Min length: `1`; Max length: `20` | — |

### `TimetableUpdateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `class_id` | anyOf: integer, null | No | — | — |
| `subject_id` | anyOf: integer, null | No | — | — |
| `teacher_id` | anyOf: integer, null | No | — | — |
| `day_of_week` | anyOf: integer, null | No | — | — |
| `start_time` | anyOf: string (time), null | No | — | — |
| `end_time` | anyOf: string (time), null | No | — | — |
| `room` | anyOf: string, null | No | — | — |
| `academic_year` | anyOf: string, null | No | — | — |

### `UpcomingInterviewSummaryItem`

A limited, applicant-safe dashboard preview of a scheduled interview.

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `id` | integer | Yes | — | Interview schedule ID. |
| `inquiry_code` | string | Yes | — | Inquiry code associated with the interview. |
| `student_name` | string | Yes | — | Applicant name; returned only with inquiries.read. |
| `schedule_date` | string (date) | Yes | — | School-local interview date. |
| `schedule_time` | string (time) | Yes | — | School-local interview start time. |
| `location` | string | Yes | — | Interview location or meeting details. |
| `mode` | string | Yes | — | Interview mode: ONLINE or OFFLINE. |

### `UserRegisterRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `first_name` | string | Yes | Min length: `1`; Max length: `100` | User's given name. |
| `last_name` | string | Yes | Min length: `1`; Max length: `100` | User's family name. |
| `email` | string | Yes | — | Unique email address used to sign in. |
| `phone` | anyOf: string, null | No | — | Optional contact phone number. |
| `password` | string | Yes | Min length: `8` | Initial password; use at least 8 characters and follow password policy. |
| `role_codes` | array of string | Yes | Min items: `1` | One or more active role codes to assign. Examples: SUPER_ADMIN, ADMIN, PRINCIPAL, TEACHER, ACCOUNTANT, ADMISSION_OFFICER, STUDENT, PARENT. Use role codes, not numeric role IDs.; Example: `['TEACHER']` |

### `ValidationError`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `loc` | array of anyOf: string, integer | Yes | — | — |
| `msg` | string | Yes | — | — |
| `type` | string | Yes | — | — |
| `input` | object | No | — | — |
| `ctx` | object | No | — | — |
