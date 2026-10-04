"""Clinic: thin in-memory coordinator (v0.4).

Holds registries and enforces the rules that need to see MORE than one object
(unique IDs, known patient/practitioner, no double-booking).  It does NOT own
validation or status logic - Patient and Appointment keep their own invariants.
No database, UI or notification logic lives here.
"""
from datetime import datetime

from appointment import Appointment, AppointmentStatus
from exceptions import DoubleBookingError, DuplicateIdError, UnknownEntityError
from patient import Patient
from practitioner import Practitioner


class Clinic:
    def __init__(self) -> None:
        self._patients: dict[str, Patient] = {}
        self._practitioners: dict[str, Practitioner] = {}
        self._appointments: dict[str, Appointment] = {}

    def register_patient(self, patient: Patient) -> None:
        if patient.patient_id in self._patients:
            raise DuplicateIdError(f"patient {patient.patient_id} already registered")
        self._patients[patient.patient_id] = patient

    def register_practitioner(self, practitioner: Practitioner) -> None:
        if practitioner.practitioner_id in self._practitioners:
            raise DuplicateIdError(
                f"practitioner {practitioner.practitioner_id} already registered")
        self._practitioners[practitioner.practitioner_id] = practitioner

    def search_patients(self, text: str) -> list[Patient]:
        return [p for p in self._patients.values() if p.matches(text)]

    def book_appointment(self, patient_id: str, practitioner_id: str,
                         start: datetime) -> Appointment:
        patient = self._patients.get(patient_id)
        if patient is None:
            raise UnknownEntityError(f"unknown patient {patient_id}")
        practitioner = self._practitioners.get(practitioner_id)
        if practitioner is None:
            raise UnknownEntityError(f"unknown practitioner {practitioner_id}")
        if any(a.is_active and a.practitioner is practitioner and a.start == start
               for a in self._appointments.values()):
            raise DoubleBookingError(
                f"{practitioner.name} already has an appointment at {start:%Y-%m-%d %H:%M}")
        appointment = Appointment(self._next_appointment_id(), patient, practitioner, start)
        self._appointments[appointment.appointment_id] = appointment
        return appointment

    def cancel_appointment(self, appointment_id: str) -> Appointment:
        appointment = self._get_appointment(appointment_id)
        appointment.cancel()  # Appointment decides whether this is legal
        return appointment

    def complete_appointment(self, appointment_id: str) -> Appointment:
        appointment = self._get_appointment(appointment_id)
        appointment.complete()
        return appointment

    def schedule_for(self, practitioner_id: str) -> list[Appointment]:
        if practitioner_id not in self._practitioners:
            raise UnknownEntityError(f"unknown practitioner {practitioner_id}")
        return sorted((a for a in self._appointments.values()
                       if a.practitioner.practitioner_id == practitioner_id),
                      key=lambda a: a.start)

    def history_for(self, patient_id: str) -> list[Appointment]:
        """All appointments for the patient, including cancelled ones (FR-11)."""
        if patient_id not in self._patients:
            raise UnknownEntityError(f"unknown patient {patient_id}")
        return sorted((a for a in self._appointments.values()
                       if a.patient.patient_id == patient_id), key=lambda a: a.start)

    def status_report(self) -> dict[str, int]:
        report = {status.value: 0 for status in AppointmentStatus}
        for a in self._appointments.values():
            report[a.status.value] += 1
        return report

    def _get_appointment(self, appointment_id: str) -> Appointment:
        try:
            return self._appointments[appointment_id]
        except KeyError:
            raise UnknownEntityError(f"unknown appointment {appointment_id}") from None

    def _next_appointment_id(self) -> str:
        return f"A{len(self._appointments) + 1:04d}"
