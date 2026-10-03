"""SmartCare v0.1 - starter prototype (Week 4, Stage 1).

STATUS_SCHEDULED = "scheduled"
STATUS_CANCELLED = "cancelled"

patients: list[dict] = []
practitioners: list[dict] = []
appointments: list[dict] = []


def reset() -> None:
    """Clear all data (used by tests and the demo)."""
    patients.clear()
    practitioners.clear()
    appointments.clear()


def add_patient(patient_id: str, name: str) -> dict:
    if not patient_id or not name:
        raise ValueError("patient id and name are required")
    if any(p["id"] == patient_id for p in patients):
        raise ValueError(f"patient id {patient_id} already exists")
    record = {"id": patient_id, "name": name}
    patients.append(record)
    return record


def add_practitioner(practitioner_id: str, name: str) -> dict:
    if not practitioner_id or not name:
        raise ValueError("practitioner id and name are required")
    if any(p["id"] == practitioner_id for p in practitioners):
        raise ValueError(f"practitioner id {practitioner_id} already exists")
    record = {"id": practitioner_id, "name": name}
    practitioners.append(record)
    return record


def find_patients(text: str) -> list[dict]:
    """Return patients whose id equals, or whose name contains, `text`."""
    text = text.lower()
    return [p for p in patients if p["id"].lower() == text or text in p["name"].lower()]


def book_appointment(patient_id: str, practitioner_id: str, when: str) -> dict:
    """Book an appointment. `when` is free text such as '2026-10-05 09:00'."""
    if not any(p["id"] == patient_id for p in patients):
        raise ValueError(f"unknown patient {patient_id}")
    if not any(p["id"] == practitioner_id for p in practitioners):
        raise ValueError(f"unknown practitioner {practitioner_id}")
    for a in appointments:
        if (a["practitioner_id"] == practitioner_id and a["when"] == when
                and a["status"] == STATUS_SCHEDULED):
            raise ValueError("practitioner already booked at that time")
    record = {
        "id": len(appointments) + 1,
        "patient_id": patient_id,
        "practitioner_id": practitioner_id,
        "when": when,
        "status": STATUS_SCHEDULED,
    }
    appointments.append(record)
    return record


def cancel_appointment(appointment_id: int) -> dict:
    """Mark an appointment as cancelled (the record is kept)."""
    for a in appointments:
        if a["id"] == appointment_id:
            a["status"] = STATUS_CANCELLED
            return a
    raise ValueError(f"unknown appointment {appointment_id}")


def list_appointments(practitioner_id: str | None = None) -> list[dict]:
    return [a for a in appointments
            if practitioner_id is None or a["practitioner_id"] == practitioner_id]


def main() -> None:
    reset()
    add_patient("P001", "Aisha Rahman")
    add_patient("P002", "Ben Carter")
    add_practitioner("D01", "Dr Mei Tanaka")
    print("Found:", find_patients("rahman"))
    a1 = book_appointment("P001", "D01", "2026-10-05 09:00")
    print("Booked:", a1)
    try:
        book_appointment("P002", "D01", "2026-10-05 09:00")
    except ValueError as err:
        print("Rejected duplicate booking ->", err)
    print("Cancelled:", cancel_appointment(a1["id"]))
    print("Rebook after cancel:", book_appointment("P002", "D01", "2026-10-05 09:00"))
    print("Schedule for D01:")
    for a in list_appointments("D01"):
        print("  ", a)


if __name__ == "__main__":
    main()
