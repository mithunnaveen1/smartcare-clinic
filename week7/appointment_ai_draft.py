"""RAW AI OUTPUT - kept unedited as evidence (Stage 4 Part D).
"""
from datetime import datetime
from enum import Enum


class AppointmentStatus(Enum):
    SCHEDULED = "SCHEDULED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class InvalidStatusTransitionError(Exception):
    """Raised when a status transition is not permitted."""


class Appointment:
    def __init__(self, appointment_id, patient, practitioner, start: datetime):
        self._appointment_id = appointment_id
        self._patient = patient
        self._practitioner = practitioner
        self._start = start
        self._status = AppointmentStatus.SCHEDULED
        self._cancelled_at = None

    @property
    def appointment_id(self):
        return self._appointment_id

    @property
    def patient(self):
        return self._patient

    @property
    def practitioner(self):
        return self._practitioner

    @property
    def start(self):
        return self._start

    @property
    def status(self) -> AppointmentStatus:
        return self._status

    @property
    def cancelled_at(self):
        return self._cancelled_at

    def cancel(self, reason: str = "") -> None:
        # Only a scheduled appointment can be cancelled.
        if self._status != AppointmentStatus.SCHEDULED:
            raise InvalidStatusTransitionError(
                f"Cannot cancel an appointment that is {self._status.value}")
        self._status = AppointmentStatus.CANCELLED
        self._cancelled_at = datetime.now()
        self._cancel_reason = reason

    def complete(self) -> None:
        # Only a scheduled appointment can be completed.
        if self._status != AppointmentStatus.SCHEDULED:
            raise InvalidStatusTransitionError(
                f"Cannot complete an appointment that is {self._status.value}")
        self._status = AppointmentStatus.COMPLETED

    def __repr__(self):
        return (f"Appointment({self._appointment_id!r}, {self._patient!r}, "
                f"{self._practitioner!r}, {self._start!r}, {self._status})")
