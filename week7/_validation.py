"""Small shared validation helper (keeps Patient/Practitioner free of duplication)."""


def require_text(value: object, field: str) -> str:
    """Return `value` stripped; raise if it is not a non-blank string."""
    if not isinstance(value, str):
        raise TypeError(f"{field} must be a string")
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field} must not be blank")
    return cleaned
