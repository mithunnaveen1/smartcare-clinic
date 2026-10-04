"""Manual behaviour checks (Stage 4 Part F): valid objects, invalid input,
cancel a scheduled appointment, attempt an illegal repeated transition."""
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from smartcare import (Clinic, DoubleBookingError, InvalidStatusTransitionError,  # noqa: E402
                       Patient, Practitioner)


def attempt(label, fn):
    try:
        result = fn()
        print(f"[OK]       {label}: {result}")
    except Exception as err:  # demo script: show every outcome
        print(f"[REJECTED] {label}: {type(err).__name__}: {err}")


clinic = Clinic()
print("--- 1. valid objects")
patient = Patient("P001", "Aisha Rahman", date(1990, 4, 12), "0412 345 678")
other = Patient("P002", "Ben Carter", date(1985, 1, 30), "0498 111 222")
doctor = Practitioner("D01", "Dr Mei Tanaka", "General Practice")
for p in (patient, other):
    clinic.register_patient(p)
clinic.register_practitioner(doctor)
print(patient, other, doctor)

print("--- 2. invalid input")
attempt("blank patient name", lambda: Patient("P003", "  ", date(1990, 1, 1), "0412 345 678"))
attempt("phone 'abc'", lambda: Patient("P003", "X", date(1990, 1, 1), "abc"))
attempt("future birth date", lambda: Patient("P003", "X", date(2999, 1, 1), "0412 345 678"))
attempt("unknown patient booking",
        lambda: clinic.book_appointment("P999", "D01", datetime(2026, 10, 5, 9, 0)))

print("--- 3. booking, double booking, cancel, illegal repeat")
appt = clinic.book_appointment("P001", "D01", datetime(2026, 10, 5, 9, 0))
print("booked:", appt)
attempt("double booking", lambda: clinic.book_appointment("P002", "D01", datetime(2026, 10, 5, 9, 0)))
attempt("cancel scheduled", lambda: clinic.cancel_appointment(appt.appointment_id))
attempt("cancel again (illegal)", lambda: clinic.cancel_appointment(appt.appointment_id))
attempt("direct status assignment", lambda: setattr(appt, "status", None))
attempt("rebook freed slot", lambda: clinic.book_appointment("P002", "D01", datetime(2026, 10, 5, 9, 0)))

print("--- 4. history and report")
print("history P001:", clinic.history_for("P001"))
print("report:", clinic.status_report())
