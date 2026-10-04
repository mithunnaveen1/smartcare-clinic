"""Patient domain class (v0.4)."""
from datetime import date, datetime

from _validation import require_text


class Patient:
    """A person registered with the clinic. Owns validation of its own data."""

    def __init__(self, patient_id: str, name: str, date_of_birth: date, phone: str) -> None:
        self._patient_id = require_text(patient_id, "patient_id")
        self._name = require_text(name, "name")
        if not isinstance(date_of_birth, date) or isinstance(date_of_birth, datetime):
            raise TypeError("date_of_birth must be a date")
        if date_of_birth > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        self._date_of_birth = date_of_birth
        self._phone = self._validate_phone(phone)

    @staticmethod
    def _validate_phone(phone: str) -> str:
        phone = require_text(phone, "phone")
        if any(not (ch.isdigit() or ch in "+-() ") for ch in phone):
            raise ValueError("phone may contain only digits, spaces and + - ( )")
        if not 8 <= sum(ch.isdigit() for ch in phone) <= 15:
            raise ValueError("phone must contain 8 to 15 digits")
        return phone

    @property
    def patient_id(self) -> str:
        return self._patient_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def date_of_birth(self) -> date:
        return self._date_of_birth

    @property
    def phone(self) -> str:
        return self._phone

    def matches(self, text: str) -> bool:
        """True if `text` equals the patient ID or is part of the name (case-insensitive)."""
        text = text.strip().lower()
        if not text:
            return False
        return text == self._patient_id.lower() or text in self._name.lower()

    def __repr__(self) -> str:
        return f"Patient({self._patient_id!r}, {self._name!r})"
