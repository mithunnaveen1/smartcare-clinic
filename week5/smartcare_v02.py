"""SmartCare v0.2 - requirements-driven prototype (Week 5, Stage 2).

Evolves the v0.1 starter so that it satisfies the acceptance criteria written
for the v0.2 Requirements Specification (FR-01..FR-12).  Still deliberately
dictionary-based: the object-oriented domain model arrives in Stages 3-4.

Changes from v0.1 (each traced to a requirement):
  * appointment time is parsed and validated as a datetime        (FR-05, BR-05)
  * double-booking is detected on the parsed time                 (FR-06, BR-02)
  * status lifecycle SCHEDULED -> COMPLETED | CANCELLED enforced  (FR-08..FR-10)
  * patient appointment history and a status report added         (FR-11, FR-12)
  * state held in a store object instead of module globals        (NFR-02 testability)
"""
from datetime import datetime

SCHEDULED, COMPLETED, CANCELLED = "SCHEDULED", "COMPLETED", "CANCELLED"
_ALLOWED = {SCHEDULED: {COMPLETED, CANCELLED}, COMPLETED: set(), CANCELLED: set()}
TIME_FORMAT = "%Y-%m-%d %H:%M"


class SmartCareStore:
    def __init__(self) -> None:
        self.patients: dict[str, dict] = {}
        self.practitioners: dict[str, dict] = {}
        self.appointments: dict[int, dict] = {}

    # FR-01 / FR-03 -----------------------------------------------------
    def register_patient(self, patient_id: str, name: str, phone: str) -> dict:
        if not patient_id.strip() or not name.strip():
            raise ValueError("patient id and name are required")
        if patient_id in self.patients:
            raise ValueError(f"patient id {patient_id} already exists")
        self.patients[patient_id] = {"id": patient_id, "name": name.strip(), "phone": phone}
        return self.patients[patient_id]

    def register_practitioner(self, practitioner_id: str, name: str, specialty: str) -> dict:
        if not practitioner_id.strip() or not name.strip():
            raise ValueError("practitioner id and name are required")
        if practitioner_id in self.practitioners:
            raise ValueError(f"practitioner id {practitioner_id} already exists")
        self.practitioners[practitioner_id] = {
            "id": practitioner_id, "name": name.strip(), "specialty": specialty}
        return self.practitioners[practitioner_id]

    # FR-02 -------------------------------------------------------------
    def search_patients(self, text: str) -> list[dict]:
        text = text.strip().lower()
        return [p for p in self.patients.values()
                if p["id"].lower() == text or (text and text in p["name"].lower())]

    # FR-05, FR-06, FR-07 -------------------------------------------------
    def book(self, patient_id: str, practitioner_id: str, when: str) -> dict:
        if patient_id not in self.patients:
            raise ValueError(f"unknown patient {patient_id}")
        if practitioner_id not in self.practitioners:
            raise ValueError(f"unknown practitioner {practitioner_id}")
        start = datetime.strptime(when, TIME_FORMAT)  # ValueError if malformed
        for a in self.appointments.values():
            if (a["practitioner_id"] == practitioner_id and a["start"] == start
                    and a["status"] == SCHEDULED):
                raise ValueError("practitioner already has an appointment at that time")
        appt_id = len(self.appointments) + 1
        self.appointments[appt_id] = {
            "id": appt_id, "patient_id": patient_id, "practitioner_id": practitioner_id,
            "start": start, "status": SCHEDULED}
        return self.appointments[appt_id]

    # FR-08, FR-09, FR-10 -------------------------------------------------
    def _change_status(self, appt_id: int, new_status: str) -> dict:
        appt = self.appointments.get(appt_id)
        if appt is None:
            raise ValueError(f"unknown appointment {appt_id}")
        if new_status not in _ALLOWED[appt["status"]]:
            raise ValueError(f"cannot change appointment from {appt['status']} to {new_status}")
        appt["status"] = new_status
        return appt

    def cancel(self, appt_id: int) -> dict:
        return self._change_status(appt_id, CANCELLED)

    def complete(self, appt_id: int) -> dict:
        return self._change_status(appt_id, COMPLETED)

    # FR-04, FR-11, FR-12 -------------------------------------------------
    def schedule_for(self, practitioner_id: str) -> list[dict]:
        return sorted((a for a in self.appointments.values()
                       if a["practitioner_id"] == practitioner_id), key=lambda a: a["start"])

    def history_for(self, patient_id: str) -> list[dict]:
        return sorted((a for a in self.appointments.values()
                       if a["patient_id"] == patient_id), key=lambda a: a["start"])

    def status_report(self) -> dict[str, int]:
        report = {SCHEDULED: 0, COMPLETED: 0, CANCELLED: 0}
        for a in self.appointments.values():
            report[a["status"]] += 1
        return report


def main() -> None:
    s = SmartCareStore()
    s.register_patient("P001", "Aisha Rahman", "0412 345 678")
    s.register_patient("P002", "Ben Carter", "0498 111 222")
    s.register_practitioner("D01", "Dr Mei Tanaka", "General Practice")
    a = s.book("P001", "D01", "2026-10-05 09:00")
    print("Booked:", a["id"], a["status"])
    try:
        s.book("P002", "D01", "2026-10-05 09:00")
    except ValueError as e:
        print("Rejected:", e)
    s.cancel(a["id"])
    try:
        s.cancel(a["id"])
    except ValueError as e:
        print("Rejected:", e)
    print("History P001:", [(x["id"], x["status"]) for x in s.history_for("P001")])
    print("Report:", s.status_report())


if __name__ == "__main__":
    main()
