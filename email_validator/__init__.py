"""Minimal stub for email validation used in tests.

This stub only performs a basic check that an email contains an '@' character.
It is sufficient for environments where the third-party `email-validator`
package cannot be installed.
"""

class EmailNotValidError(ValueError):
    """Exception raised when an email address fails validation."""


class ValidatedEmail:
    """Lightweight replacement for email_validator.ValidatedEmail."""

    __slots__ = (
        "local_part",
        "domain",
        "email",
        "ascii_email",
        "normalized",
        "normalized_email",
    )

    def __init__(self, local_part: str, domain: str, normalized_email: str):
        self.local_part = local_part
        self.domain = domain
        self.email = normalized_email
        self.ascii_email = normalized_email
        self.normalized = normalized_email
        self.normalized_email = normalized_email

    def __getitem__(self, index: int):
        if index == 0:
            return self.local_part
        if index == 1:
            return self.normalized
        raise IndexError(index)

    def __iter__(self):
        yield self.local_part
        yield self.normalized


def validate_email(email: str, *_args, **_kwargs):
    """Validate an email address using a minimal heuristic.

    Args:
        email: The email address to validate.

    Returns:
        A tuple similar to the real library: (info, normalized_email).

    Raises:
        EmailNotValidError: If the email is empty or missing an '@'.
    """
    if not email or "@" not in email:
        raise EmailNotValidError("Invalid email address format")

    local_part, domain = email.split("@", 1)
    normalized_domain = domain.lower()
    normalized_email = f"{local_part}@{normalized_domain}"

    return ValidatedEmail(local_part, normalized_domain, normalized_email)


__all__ = ["EmailNotValidError", "validate_email"]
