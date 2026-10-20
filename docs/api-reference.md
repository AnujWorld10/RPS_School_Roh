# API Reference

> Generated from the application's FastAPI OpenAPI schema. Regenerate after API changes with `python scripts/generate_api_reference.py`.

The OpenAPI schema at `/openapi.json` and interactive `/docs` are the runtime contract. This file provides a browsable snapshot of every operation, its parameters, request and response schemas, and the field constraints exposed by OpenAPI. The shared response envelopes and route permissions are documented in [the technical guide](technical-documentation.md#8-authentication--authorization).

**Operations:** 76

## Operations

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
      "documents_required": 6
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
      "documents_required": 6
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
      "section": "A",
      "academic_year": "2026-2027",
      "status": "submitted",
      "permanent_address": "12 School Road, Pune",
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
    "section": "A",
    "academic_year": "2026-2027",
    "status": "submitted",
    "permanent_address": "12 School Road, Pune",
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
    "section": "A",
    "academic_year": "2026-2027",
    "status": "submitted",
    "permanent_address": "12 School Road, Pune",
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
    "section": "A",
    "academic_year": "2026-2027",
    "status": "submitted",
    "permanent_address": "12 School Road, Pune",
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

### `POST /api/v1/inquiry-admissions/{admission_id}/documents`

Upload Admission Document

**Group:** `admissions`

**OpenAPI authentication:** `HTTPBearer`

**Authorization requirement:** Requires permission `admissions.update`.

**Parameters**

| Name | Location | Required | Type and constraints | Description |
|---|---|---:|---|---|
| `admission_id` | path | Yes | integer | — |

**Request body**

Required: Yes
- `multipart/form-data`: [`Body_upload_admission_document_api_v1_inquiry_admissions__admission_id__documents_post`](#body_upload_admission_document_api_v1_inquiry_admissions__admission_id__documents_post)

For multipart requests, send the listed fields as form parts. The `file` part must contain the selected local file, not a JSON-encoded path.

**Illustrative success response**

HTTP `200`. IDs, dates, request IDs, and tokens below are illustrative; the token strings are not valid credentials.

```json
{
  "success": true,
  "message": "Document uploaded successfully",
  "data": {
    "id": 1,
    "admission_id": 1,
    "document_type": "progress_report",
    "file_name": "progress-report.pdf",
    "file_path": "uploads/admissions/1/progress-report.pdf",
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
    "file_path": "uploads/admissions/1/progress-report.pdf",
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
    "section": "A",
    "academic_year": "2026-2027",
    "status": "submitted",
    "permanent_address": "12 School Road, Pune",
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
    "section": "A",
    "academic_year": "2026-2027",
    "status": "submitted",
    "permanent_address": "12 School Road, Pune",
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
    "admission_code": "ADM202600055",
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

### `AttendanceCreateRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `attendance_date` | string (date) | Yes | — | Date for this attendance record.; Example: `2026-10-19` |
| `status` | [`AttendanceStatus`](#attendancestatus) | Yes | — | Attendance state: present, absent, leave, or half_day. |
| `remarks` | anyOf: string, null | No | — | Optional attendance note. |

### `AttendanceStatus`

**Allowed values:** `present`, `absent`, `leave`, `half_day`

### `Body_submit_admission_api_v1_public_student_admission_post`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `inquiry_code` | string | Yes | Min length: `5`; Max length: `20` | Inquiry tracking code returned when the inquiry was submitted.; Example: `INQ202600007` |
| `email` | string (email) | Yes | — | Email address supplied with the original inquiry. |
| `parent_mobile` | string | Yes | Min length: `5`; Max length: `30` | Parent/guardian mobile number supplied with the original inquiry. |
| `class_id` | integer | Yes | — | Catalog ID of the class requested for admission.; Example: `1` |
| `academic_year` | string | Yes | Min length: `4`; Max length: `20` | Academic year for admission.; Example: `2026-2027` |
| `section` | anyOf: string, null | No | — | Optional section within the selected class. |
| `permanent_address` | anyOf: string, null | No | — | Optional permanent residential address. |

### `Body_upload_admission_document_api_v1_inquiry_admissions__admission_id__documents_post`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `document_type` | string | Yes | — | Document category: progress_report, transfer_certificate, migration_certificate, character_certificate, student_aadhar, or parent_aadhar. |
| `file` | string | Yes | — | Document file to upload (PDF, JPG, JPEG, or PNG). |

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

### `DocumentVerifyRequest`

Staff verification of a single document.

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `rejection_reason` | anyOf: string, null | No | — | Reason for rejecting the document; required when verification status is set to REJECTED. |

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

### `LogoutRequest`

| Property | Type | Required | Constraints | Description |
|---|---|---:|---|---|
| `refresh_token` | string | Yes | — | Refresh token to revoke. |

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
