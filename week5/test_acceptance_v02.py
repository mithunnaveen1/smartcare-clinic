"""Executable Given-When-Then acceptance criteria for SmartCare v0.2.

Each test method name carries the acceptance-criterion ID (AC-xx) and the
requirement(s) it verifies, giving traceability: FR -> AC -> test.
"""
import unittest

from smartcare_v02 import CANCELLED, COMPLETED, SCHEDULED, SmartCareStore


class AcceptanceBase(unittest.TestCase):
    def setUp(self):
        self.s = SmartCareStore()
        self.s.register_patient("P001", "Aisha Rahman", "0412 345 678")
        self.s.register_patient("P002", "Ben Carter", "0498 111 222")
        self.s.register_practitioner("D01", "Dr Mei Tanaka", "General Practice")
        self.s.register_practitioner("D02", "Dr Luis Ortega", "General Practice")


class TestAcceptanceCriteria(AcceptanceBase):
    def test_AC01_successful_booking_FR05(self):
        # GIVEN registered patient P001 and practitioner D01 free at 09:00
        # WHEN the receptionist books the appointment
        a = self.s.book("P001", "D01", "2026-10-05 09:00")
        # THEN it is created with status SCHEDULED
        self.assertEqual(a["status"], SCHEDULED)

    def test_AC02_double_booking_rejected_FR06(self):
        # GIVEN D01 has a SCHEDULED appointment at 09:00
        self.s.book("P001", "D01", "2026-10-05 09:00")
        # WHEN another booking for D01 at 09:00 is attempted (any text form)
        # THEN it is rejected and no second appointment exists
        with self.assertRaises(ValueError):
            self.s.book("P002", "D01", "2026-10-05 09:00")
        self.assertEqual(len(self.s.appointments), 1)

    def test_AC03_cancel_scheduled_retains_record_FR08(self):
        # GIVEN a SCHEDULED appointment
        a = self.s.book("P001", "D01", "2026-10-05 09:00")
        # WHEN it is cancelled
        self.s.cancel(a["id"])
        # THEN status is CANCELLED, the record remains, and the slot is free again
        self.assertEqual(self.s.appointments[a["id"]]["status"], CANCELLED)
        self.s.book("P002", "D01", "2026-10-05 09:00")

    def test_AC04_cancel_already_cancelled_rejected_FR10(self):
        # GIVEN a CANCELLED appointment
        a = self.s.book("P001", "D01", "2026-10-05 09:00")
        self.s.cancel(a["id"])
        # WHEN cancellation is attempted again
        # THEN it is rejected and the status stays CANCELLED
        with self.assertRaises(ValueError):
            self.s.cancel(a["id"])
        self.assertEqual(a["status"], CANCELLED)

    def test_AC05_patient_search_no_match_FR02(self):
        # GIVEN registered patients
        # WHEN staff search for a name that does not exist
        # THEN an empty result is returned (not an error or wrong patient)
        self.assertEqual(self.s.search_patients("Nobody"), [])
        self.assertEqual([p["id"] for p in self.s.search_patients("rahman")], ["P001"])

    def test_AC06_practitioner_schedule_only_own_FR04(self):
        # GIVEN appointments for D01 and D02
        self.s.book("P001", "D01", "2026-10-05 10:00")
        self.s.book("P002", "D01", "2026-10-05 09:00")
        self.s.book("P001", "D02", "2026-10-05 09:00")
        # WHEN D01's schedule is requested
        sched = self.s.schedule_for("D01")
        # THEN only D01's appointments appear, in time order
        self.assertEqual([a["start"].hour for a in sched], [9, 10])
        self.assertTrue(all(a["practitioner_id"] == "D01" for a in sched))


class TestOtherRequirements(AcceptanceBase):
    def test_FR07_unknown_patient_or_practitioner_rejected(self):
        with self.assertRaises(ValueError):
            self.s.book("P999", "D01", "2026-10-05 09:00")
        with self.assertRaises(ValueError):
            self.s.book("P001", "D99", "2026-10-05 09:00")

    def test_FR05_malformed_time_rejected(self):
        with self.assertRaises(ValueError):
            self.s.book("P001", "D01", "tomorrow")

    def test_FR09_complete_scheduled_then_cannot_cancel_FR10(self):
        a = self.s.book("P001", "D01", "2026-10-05 09:00")
        self.s.complete(a["id"])
        self.assertEqual(a["status"], COMPLETED)
        with self.assertRaises(ValueError):
            self.s.cancel(a["id"])

    def test_FR11_history_includes_cancelled(self):
        a = self.s.book("P001", "D01", "2026-10-05 09:00")
        self.s.cancel(a["id"])
        self.s.book("P001", "D02", "2026-10-06 09:00")
        self.assertEqual([x["status"] for x in self.s.history_for("P001")],
                         [CANCELLED, SCHEDULED])

    def test_FR12_status_report_counts(self):
        a = self.s.book("P001", "D01", "2026-10-05 09:00")
        b = self.s.book("P002", "D01", "2026-10-05 10:00")
        self.s.book("P001", "D02", "2026-10-05 11:00")
        self.s.cancel(a["id"])
        self.s.complete(b["id"])
        self.assertEqual(self.s.status_report(),
                         {SCHEDULED: 1, COMPLETED: 1, CANCELLED: 1})

    def test_FR01_duplicate_patient_id_rejected_NFR01(self):
        with self.assertRaises(ValueError):
            self.s.register_patient("P001", "Someone Else", "0400 000 000")

    def test_equivalent_time_forms_now_detected_BR05(self):
        # v0.1 weakness fixed: '9:00' and '09:00' are the same slot
        self.s.book("P001", "D01", "2026-10-05 09:00")
        with self.assertRaises(ValueError):
            self.s.book("P002", "D01", "2026-10-05 9:00")


if __name__ == "__main__":
    unittest.main(verbosity=2)
