"""Appointment domain class and lifecycle (v0.4).

Lifecycle:  SCHEDULED --cancel()--> CANCELLED
            SCHEDULED --complete()--> COMPLETED
CANCELLED and COMPLETED are terminal.  Cancelled appointments remain as objects
(FR-08, FR-11).  Only this class may change its own status (FR-10).
"""
from datetime import datetime
from enum import Enum

from exceptions import InvalidStatusTransitionError
from _validation import require_text
from patient import Patient
from practitioner import Practitioner


class AppointmentStatus(Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


_ALLOWED_TRANSITIONS = {
    AppointmentStatus.SCHEDULED: frozenset(
        {AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED}),
    AppointmentStatus.CANCELLED: frozenset(),
    AppointmentStatus.COMPLETED: frozenset(),
}


class Appointment:
    """One patient seeing one practitioner at a start time."""

    def __init__(self, appointment_id: str, patient: Patient,
                 practitioner: Practitioner, start: datetime) -> None:
        self._appointment_id = require_text(appointment_id, "appointment_id")
        if not isinstance(patient, Patient):
            raise TypeError("patient must be a Patient")
        if not isinstance(practitioner, Practitioner):
            raise TypeError("practitioner must be a Practitioner")
        if not isinstance(start, datetime):
            raise TypeError("start must be a datetime")
        self._patient = patient
        self._practitioner = practitioner
        self._start = start
        self._status = AppointmentStatus.SCHEDULED

    @property
    def appointment_id(self) -> str:
        return self._appointment_id

    @property
    def patient(self) -> Patient:
        return self._patient

    @property
    def practitioner(self) -> Practitioner:
        return self._practitioner

    @property
    def start(self) -> datetime:
        return self._start

    @property
    def status(self) -> AppointmentStatus:
        return self._status

    @property
    def is_active(self) -> bool:
        """True while the appointment still occupies the practitioner's slot."""
        return self._status is AppointmentStatus.SCHEDULED

    def cancel(self) -> None:
        self._transition_to(AppointmentStatus.CANCELLED)

    def complete(self) -> None:
        self._transition_to(AppointmentStatus.COMPLETED)

    def _transition_to(self, new_status: AppointmentStatus) -> None:
        if new_status not in _ALLOWED_TRANSITIONS[self._status]:
            raise InvalidStatusTransitionError(
                f"cannot change appointment {self._appointment_id} "
                f"from {self._status.value} to {new_status.value}")
        self._status = new_status

    def __repr__(self) -> str:
        return (f"Appointment({self._appointment_id!r}, {self._patient.patient_id!r}, "
                f"{self._practitioner.practitioner_id!r}, {self._start:%Y-%m-%d %H:%M}, "
                f"{self._status.value})")
