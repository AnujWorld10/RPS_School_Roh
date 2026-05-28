"""
Email validation for API schemas.

Pydantic ``EmailStr`` rejects special-use TLDs such as ``.local`` (RFC 6762).
This module provides ``AppEmail``, which accepts normal addresses used in
development and production (including ``user@school.local``).
"""

import re
from typing import Annotated

from pydantic import BeforeValidator

# Practical format check: local-part @ domain with at least one dot in the domain.
_EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def _validate_app_email(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Email must be a string")
    normalized = value.strip()
    if not normalized:
        raise ValueError("Email is required")
    if not _EMAIL_RE.match(normalized):
        raise ValueError("Invalid email address")
    return normalized


AppEmail = Annotated[str, BeforeValidator(_validate_app_email)]
