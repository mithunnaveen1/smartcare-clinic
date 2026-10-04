"""SmartCare v0.3 - Python class skeletons (Week 6, Stage 3).

Skeletons only: structure and signatures derived from the v0.3 UML domain
model.  Behaviour is intentionally NOT implemented yet (Stage 4).  Methods
raise NotImplementedError so nobody mistakes a stub for working logic.
"""
from datetime import date, datetime
from enum import Enum


class AppointmentStatus(Enum):
    """Lifecycle states of an appointment (FR-08, FR-09, FR-10)."""
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class InvalidStatusTransitionError(Exception):
    """Raised when an illegal status change is attempted (FR-10)."""


class Patient:
    """A person registered with the clinic (FR-01, FR-02, FR-11)."""

    def __init__(self, patient_id: str, name: str, date_of_birth: date, phone: str) -> None:
        self.patient_id = patient_id
        self.name = name
        self.date_of_birth = date_of_birth
        self.phone = phone

    def matches(self, text: str) -> bool:
        """True if `text` identifies this patient by id or name (FR-02)."""
        raise NotImplementedError


class Practitioner:
    """A GP who provides consultations (FR-03, FR-04)."""

    def __init__(self, practitioner_id: str, name: str, specialty: str) -> None:
        self.practitioner_id = practitioner_id
        self.name = name
        self.specialty = specialty


class Appointment:
    """A booking of one patient with one practitioner at a start time (FR-05..FR-10)."""

    def __init__(self, appointment_id: str, patient: Patient,
                 practitioner: Practitioner, start: datetime) -> None:
        self.appointment_id = appointment_id
        self.patient = patient
        self.practitioner = practitioner
        self.start = start
        self.status = AppointmentStatus.SCHEDULED

    @property
    def is_active(self) -> bool:
        raise NotImplementedError

    def cancel(self) -> None:
        raise NotImplementedError

    def complete(self) -> None:
        raise NotImplementedError


class Clinic:
    """Thin coordinator/registry: lookups and cross-object rules (FR-02, FR-04, FR-06, FR-07, FR-11, FR-12)."""

    def __init__(self) -> None:
        self._patients: dict[str, Patient] = {}
        self._practitioners: dict[str, Practitioner] = {}
        self._appointments: list[Appointment] = []

    def register_patient(self, patient: Patient) -> None:
        raise NotImplementedError

    def register_practitioner(self, practitioner: Practitioner) -> None:
        raise NotImplementedError

    def search_patients(self, text: str) -> list[Patient]:
        raise NotImplementedError

    def book_appointment(self, appointment_id: str, patient_id: str,
                         practitioner_id: str, start: datetime) -> Appointment:
        raise NotImplementedError

    def schedule_for(self, practitioner_id: str) -> list[Appointment]:
        raise NotImplementedError

    def history_for(self, patient_id: str) -> list[Appointment]:
        raise NotImplementedError

    def status_report(self) -> dict[str, int]:
        raise NotImplementedError
