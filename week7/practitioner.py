"""Practitioner domain class (v0.4). Identity only - no persistence or scheduling logic."""
from _validation import require_text


class Practitioner:
    """A GP who provides consultations."""

    def __init__(self, practitioner_id: str, name: str,
                 specialty: str = "General Practice") -> None:
        self._practitioner_id = require_text(practitioner_id, "practitioner_id")
        self._name = require_text(name, "name")
        self._specialty = require_text(specialty, "specialty")

    @property
    def practitioner_id(self) -> str:
        return self._practitioner_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def specialty(self) -> str:
        return self._specialty

    def __repr__(self) -> str:
        return f"Practitioner({self._practitioner_id!r}, {self._name!r})"
