# Duplicate Student Inquiry Detection - Implementation Guide

## Overview

This document explains the duplicate student inquiry detection mechanism implemented to prevent duplicate submissions when users click the submit button multiple times.

## Problem Statement

When a student submits an inquiry form via the public endpoint, the system was creating duplicate records if the submit button was clicked multiple times. This resulted in:
- Duplicate processing workload
- Confusion in the admission pipeline
- Parent dissatisfaction due to duplicate confirmation messages

## Solution Architecture

### Validation Strategy

The system validates duplicate inquiries using a **combination of 3 identifiers**:

1. **Student's First Name & Last Name** (case-insensitive)
2. **Father's Name** (case-insensitive)
3. **Student's Date of Birth** (exact match)

This combination is:
- ✅ Unique enough to prevent accidental duplicates
- ✅ Scalable for multi-child families (different children have different DOB or name)
- ✅ Resistant to typos due to case-insensitive matching
- ✅ Industry-standard for student identity verification

### Why This Approach?

**Not email-only or phone-only:**
- A parent may have multiple email addresses or phone numbers
- Multiple children cannot share an email/phone with different DOB

**Not just name + DOB:**
- Father's name adds a critical uniqueness check
- Prevents false duplicates in cases of common names (e.g., "Ahmed Khan" with "Mohammed Khan" vs "Ahmed Khan" with "Hassan Khan")

**Case-insensitive comparison:**
- Users may enter names with different capitalization
- Protects against variations like "KHAN" vs "khan" vs "Khan"

## Implementation Details

### 1. Repository Layer: `find_duplicate_inquiry()`

**File:** [app/repositories/inquiries.py](app/repositories/inquiries.py)

```python
def find_duplicate_inquiry(
    self,
    first_name: str,
    last_name: str,
    father_name: str,
    date_of_birth: date,
) -> StudentInquiry | None:
    """
    Check for duplicate inquiry using combination of student identifiers.
    
    Query:
    WHERE LOWER(first_name) = LOWER(:first_name)
    AND LOWER(last_name) = LOWER(:last_name)
    AND LOWER(father_name) = LOWER(:father_name)
    AND date_of_birth = :dob
    AND status NOT IN ('REJECTED', 'INTERVIEW_FAIL')
    """
```

**Key Features:**
- Case-insensitive name matching using SQLAlchemy's `ilike()`
- Exact DOB matching to ensure true identity
- **Excludes REJECTED and INTERVIEW_FAIL statuses** to allow reapplication
- Returns the existing inquiry if found, `None` otherwise

**Status Exclusion Logic:**
- `REJECTED`: Parent may want to reapply with updated information
- `INTERVIEW_FAIL`: Student should be allowed to attempt again
- All other active statuses (PENDING, UNDER_REVIEW, PROCESSING, etc.): Block duplicate

### 2. Service Layer: `create_public_inquiry()`

**File:** [app/services/inquiries.py](app/services/inquiries.py)

The service now performs duplicate validation **before** creating the inquiry:

```python
def create_public_inquiry(self, payload: PublicInquiryCreateRequest, request: Request) -> StudentInquiry:
    """
    Create a new inquiry from the public form.
    
    Validates no duplicate inquiry exists using:
    - Student first_name, last_name
    - Father name
    - Date of birth (case-insensitive name matching)
    """
    # Check for duplicate inquiry before proceeding
    existing_inquiry = self.repo.find_duplicate_inquiry(
        first_name=payload.first_name,
        last_name=payload.last_name,
        father_name=payload.father_name,
        date_of_birth=payload.dob,
    )
    if existing_inquiry:
        raise ConflictException(
            "Student inquiry already exists. Please contact school administration."
        )
    
    # Proceed with inquiry creation...
```

### 3. Error Response: HTTP 409 Conflict

**Exception Type:** `ConflictException` (app/core/exceptions.py)

**HTTP Status:** `409 Conflict`

**Response Format:**
```json
{
  "success": false,
  "message": "Student inquiry already exists. Please contact school administration.",
  "code": "RESOURCE_CONFLICT",
  "status_code": 409,
  "data": null
}
```

This is the appropriate HTTP status code for duplicate resource creation attempts.

## Database Query Example

The actual SQL query executed by SQLAlchemy:

```sql
SELECT *
FROM student_inquiries
WHERE LOWER(first_name) = LOWER('Ahmed')
  AND LOWER(last_name) = LOWER('Khan')
  AND LOWER(father_name) = LOWER('Mohammed Khan')
  AND date_of_birth = '2015-06-15'
  AND status NOT IN ('REJECTED', 'INTERVIEW_FAIL')
LIMIT 1;
```

## Testing

Comprehensive unit tests are provided in:
**File:** [app/tests/unit/test_duplicate_inquiry_detection.py](app/tests/unit/test_duplicate_inquiry_detection.py)

### Test Coverage:

1. **Exact Match Detection**
   - Confirms duplicate is found with identical names and DOB

2. **Case-Insensitive Matching**
   - Tests with different case variations (AHMED vs ahmed, KHAN vs khan)

3. **Different Names Not Duplicates**
   - Confirms that different first names are not flagged as duplicates
   - Validates multi-child family scenario

4. **Different DOB Not Duplicates**
   - Confirms that same name + different DOB = allowed (siblings)

5. **Status Exclusion - REJECTED**
   - Confirms REJECTED inquiries don't block reapplication

6. **Status Exclusion - INTERVIEW_FAIL**
   - Confirms INTERVIEW_FAIL inquiries don't block reapplication

7. **Service Integration Test**
   - Confirms `InquiryService.create_public_inquiry()` raises `ConflictException`

## Usage Example

### Frontend Implementation

When form submission fails with HTTP 409:

```javascript
async function submitInquiry(formData) {
  try {
    const response = await fetch('/api/v1/public/student/inquiry', {
      method: 'POST',
      body: JSON.stringify(formData),
      headers: { 'Content-Type': 'application/json' }
    });
    
    if (response.status === 409) {
      // Conflict - duplicate submission
      showErrorMessage(
        "Student inquiry already exists. " +
        "Please contact school administration."
      );
      disableSubmitButton();
      return;
    }
    
    if (!response.ok) throw new Error('Submission failed');
    
    const data = await response.json();
    // Success handling...
  } catch (error) {
    showErrorMessage("An error occurred");
  }
}
```

### Implementation Notes

1. **Idempotent Button Handling**: Disable the submit button after first click
2. **User Feedback**: Show clear message if duplicate is detected
3. **No Automatic Retry**: User should contact admin for duplicate inquiries
4. **Email Tracking**: Admin can look up status using inquiry_code

## Migration & Deployment

### Prerequisites
- No database schema changes required
- Existing inquiries are not affected
- The check only applies to new submissions

### Deployment Steps
1. Deploy code changes
2. No migrations needed
3. Monitor logs for duplicate detection events
4. Test with duplicate submissions

## Performance Considerations

### Query Optimization
- The query uses indexed columns: `first_name`, `last_name`, `father_name`, `date_of_birth`, `status`
- SQLAlchemy's `ilike()` uses database-level case-insensitive comparison
- Single `LIMIT 1` ensures early termination once a match is found

### Recommended Indexes
Current indexes should be sufficient, but if needed:
```sql
CREATE INDEX idx_inquiry_duplicate_check 
ON student_inquiries (
  first_name, 
  last_name, 
  father_name, 
  date_of_birth, 
  status
);
```

## FAQ

### Q: Can siblings submit inquiries?
**A:** Yes! Different children have different first names or DOB, so they won't be flagged as duplicates.

### Q: What if a rejected inquiry needs reapplication?
**A:** REJECTED inquiries are excluded from duplicate detection, so the family can resubmit immediately.

### Q: What if names have minor typos?
**A:** Case-insensitive matching handles capitalization differences. For spelling variations, the parent should contact the admin.

### Q: What if the parent has twins?
**A:** Twins have the same DOB but different first names, so they'll be treated as separate inquiries (correctly).

### Q: Can we add phone number/email to the duplicate check?
**A:** Not recommended - same parent, multiple contact methods. The current 3-field combination is optimal.

## Related Files

- **Repository:** [app/repositories/inquiries.py](app/repositories/inquiries.py)
- **Service:** [app/services/inquiries.py](app/services/inquiries.py)
- **Routes:** [app/api/v1/public/student/routes.py](app/api/v1/public/student/routes.py)
- **Models:** [app/models/student_inquiry.py](app/models/student_inquiry.py)
- **Exceptions:** [app/core/exceptions.py](app/core/exceptions.py)
- **Tests:** [app/tests/unit/test_duplicate_inquiry_detection.py](app/tests/unit/test_duplicate_inquiry_detection.py)

## Summary

The duplicate inquiry detection mechanism:
✅ **Prevents accidental double-submissions**
✅ **Supports multi-child families**
✅ **Allows reapplication after rejection**
✅ **Uses industry-standard identity verification**
✅ **Returns appropriate HTTP 409 Conflict status**
✅ **Fully tested and documented**
