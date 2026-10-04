"""Unit tests for the SmartCare domain layer (Patient, Practitioner, Appointment, Clinic)."""
import unittest
from datetime import date, datetime, timedelta

from smartcare import (Appointment, AppointmentStatus, Clinic, DoubleBookingError,
                       DuplicateIdError, InvalidStatusTransitionError, Patient,
                       Practitioner, UnknownEntityError)

DOB = date(1990, 4, 12)
START = datetime(2026, 10, 5, 9, 0)


def make_patient(pid="P001", name="Aisha Rahman"):
    return Patient(pid, name, DOB, "0412 345 678")


def make_practitioner(did="D01", name="Dr Mei Tanaka"):
    return Practitioner(did, name, "General Practice")


class TestPatient(unittest.TestCase):
    def test_valid_patient_trims_text(self):
        p = Patient("  P001 ", " Aisha Rahman ", DOB, "0412 345 678")
        self.assertEqual((p.patient_id, p.name), ("P001", "Aisha Rahman"))

    def test_blank_id_or_name_rejected(self):
        with self.assertRaises(ValueError):
            Patient("  ", "A", DOB, "0412 345 678")
        with self.assertRaises(ValueError):
            Patient("P1", "", DOB, "0412 345 678")

    def test_wrong_types_rejected(self):
        with self.assertRaises(TypeError):
            Patient(1, "A", DOB, "0412 345 678")
        with self.assertRaises(TypeError):
            Patient("P1", "A", "1990-04-12", "0412 345 678")
        with self.assertRaises(TypeError):
            Patient("P1", "A", datetime(1990, 4, 12), "0412 345 678")

    def test_future_birth_date_rejected(self):
        with self.assertRaises(ValueError):
            Patient("P1", "A", date.today() + timedelta(days=1), "0412 345 678")

    def test_invalid_phone_rejected(self):
        for bad in ("abc", "123", "04123-45-678x", ""):
            with self.subTest(phone=bad), self.assertRaises(ValueError):
                Patient("P1", "A", DOB, bad)

    def test_state_is_read_only(self):
        p = make_patient()
        with self.assertRaises(AttributeError):
            p.patient_id = "X"
        with self.assertRaises(AttributeError):
            p.name = "X"

    def test_matches_by_id_or_partial_name_case_insensitive(self):
        p = make_patient()
        self.assertTrue(p.matches("p001"))
        self.assertTrue(p.matches("RAHMAN"))
        self.assertFalse(p.matches("carter"))
        self.assertFalse(p.matches("   "))


class TestPractitioner(unittest.TestCase):
    def test_valid_practitioner_default_specialty(self):
        d = Practitioner("D01", "Dr Mei Tanaka")
        self.assertEqual(d.specialty, "General Practice")

    def test_blank_fields_rejected(self):
        with self.assertRaises(ValueError):
            Practitioner("", "Dr X")
        with self.assertRaises(ValueError):
            Practitioner("D1", " ")
        with self.assertRaises(ValueError):
            Practitioner("D1", "Dr X", "")

    def test_read_only(self):
        with self.assertRaises(AttributeError):
            make_practitioner().name = "Dr Y"


class TestAppointment(unittest.TestCase):
    def setUp(self):
        self.appt = Appointment("A0001", make_patient(), make_practitioner(), START)

    def test_new_appointment_is_scheduled_and_active(self):
        self.assertIs(self.appt.status, AppointmentStatus.SCHEDULED)
        self.assertTrue(self.appt.is_active)

    def test_cancel_scheduled(self):
        self.appt.cancel()
        self.assertIs(self.appt.status, AppointmentStatus.CANCELLED)
        self.assertFalse(self.appt.is_active)

    def test_illegal_repeated_cancel(self):
        self.appt.cancel()
        with self.assertRaises(InvalidStatusTransitionError):
            self.appt.cancel()
        self.assertIs(self.appt.status, AppointmentStatus.CANCELLED)

    def test_complete_then_cancel_is_illegal(self):
        self.appt.complete()
        self.assertIs(self.appt.status, AppointmentStatus.COMPLETED)
        with self.assertRaises(InvalidStatusTransitionError):
            self.appt.cancel()

    def test_cancelled_cannot_be_completed(self):
        self.appt.cancel()
        with self.assertRaises(InvalidStatusTransitionError):
            self.appt.complete()

    def test_status_cannot_be_set_directly(self):
        with self.assertRaises(AttributeError):
            self.appt.status = AppointmentStatus.COMPLETED

    def test_constructor_rejects_bad_arguments(self):
        with self.assertRaises(TypeError):
            Appointment("A1", "P001", make_practitioner(), START)
        with self.assertRaises(TypeError):
            Appointment("A1", make_patient(), "D01", START)
        with self.assertRaises(TypeError):
            Appointment("A1", make_patient(), make_practitioner(), "2026-10-05")
        with self.assertRaises(ValueError):
            Appointment(" ", make_patient(), make_practitioner(), START)

    def test_no_inheritance_from_patient_or_practitioner(self):
        self.assertNotIsInstance(self.appt, Patient)
        self.assertNotIsInstance(self.appt, Practitioner)


class TestClinic(unittest.TestCase):
    def setUp(self):
        self.clinic = Clinic()
        self.clinic.register_patient(make_patient("P001", "Aisha Rahman"))
        self.clinic.register_patient(make_patient("P002", "Ben Carter"))
        self.clinic.register_practitioner(make_practitioner("D01"))
        self.clinic.register_practitioner(make_practitioner("D02", "Dr Luis Ortega"))

    def test_duplicate_ids_rejected(self):
        with self.assertRaises(DuplicateIdError):
            self.clinic.register_patient(make_patient("P001", "Other"))
        with self.assertRaises(DuplicateIdError):
            self.clinic.register_practitioner(make_practitioner("D01"))

    def test_search(self):
        self.assertEqual([p.patient_id for p in self.clinic.search_patients("carter")], ["P002"])
        self.assertEqual(self.clinic.search_patients("nobody"), [])

    def test_book_generates_ids_and_schedules(self):
        a = self.clinic.book_appointment("P001", "D01", START)
        b = self.clinic.book_appointment("P002", "D01", START + timedelta(hours=1))
        self.assertEqual((a.appointment_id, b.appointment_id), ("A0001", "A0002"))
        self.assertIs(a.status, AppointmentStatus.SCHEDULED)

    def test_double_booking_rejected(self):
        self.clinic.book_appointment("P001", "D01", START)
        with self.assertRaises(DoubleBookingError):
            self.clinic.book_appointment("P002", "D01", START)
        self.assertEqual(len(self.clinic.schedule_for("D01")), 1)

    def test_same_time_different_practitioner_allowed(self):
        self.clinic.book_appointment("P001", "D01", START)
        self.clinic.book_appointment("P002", "D02", START)

    def test_unknown_patient_or_practitioner(self):
        with self.assertRaises(UnknownEntityError):
            self.clinic.book_appointment("P999", "D01", START)
        with self.assertRaises(UnknownEntityError):
            self.clinic.book_appointment("P001", "D99", START)

    def test_cancel_retains_record_and_frees_slot(self):
        a = self.clinic.book_appointment("P001", "D01", START)
        self.clinic.cancel_appointment(a.appointment_id)
        self.assertIn(a, self.clinic.history_for("P001"))
        self.clinic.book_appointment("P002", "D01", START)  # slot free again

    def test_cancel_twice_raises_and_unknown_id_raises(self):
        a = self.clinic.book_appointment("P001", "D01", START)
        self.clinic.cancel_appointment(a.appointment_id)
        with self.assertRaises(InvalidStatusTransitionError):
            self.clinic.cancel_appointment(a.appointment_id)
        with self.assertRaises(UnknownEntityError):
            self.clinic.cancel_appointment("A9999")

    def test_schedule_sorted_and_only_that_practitioner(self):
        self.clinic.book_appointment("P001", "D01", START + timedelta(hours=1))
        self.clinic.book_appointment("P002", "D01", START)
        self.clinic.book_appointment("P001", "D02", START)
        sched = self.clinic.schedule_for("D01")
        self.assertEqual([a.start.hour for a in sched], [9, 10])
        self.assertTrue(all(a.practitioner.practitioner_id == "D01" for a in sched))

    def test_history_includes_all_statuses(self):
        a = self.clinic.book_appointment("P001", "D01", START)
        b = self.clinic.book_appointment("P001", "D02", START + timedelta(days=1))
        self.clinic.cancel_appointment(a.appointment_id)
        self.clinic.complete_appointment(b.appointment_id)
        self.assertEqual([x.status.value for x in self.clinic.history_for("P001")],
                         ["CANCELLED", "COMPLETED"])

    def test_status_report(self):
        a = self.clinic.book_appointment("P001", "D01", START)
        b = self.clinic.book_appointment("P002", "D01", START + timedelta(hours=1))
        self.clinic.book_appointment("P001", "D02", START)
        self.clinic.cancel_appointment(a.appointment_id)
        self.clinic.complete_appointment(b.appointment_id)
        self.assertEqual(self.clinic.status_report(),
                         {"SCHEDULED": 1, "COMPLETED": 1, "CANCELLED": 1})

    def test_empty_report_has_all_statuses(self):
        self.assertEqual(self.clinic.status_report(),
                         {"SCHEDULED": 0, "COMPLETED": 0, "CANCELLED": 0})


if __name__ == "__main__":
    unittest.main()
