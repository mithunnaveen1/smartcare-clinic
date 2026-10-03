"""Tests for the v0.1 starter prototype (normal AND unusual input)."""
import unittest

import starter_prototype as sc


class TestStarterPrototype(unittest.TestCase):
    def setUp(self):
        sc.reset()
        sc.add_patient("P001", "Aisha Rahman")
        sc.add_patient("P002", "Ben Carter")
        sc.add_practitioner("D01", "Dr Mei Tanaka")

    # ---- normal input ------------------------------------------------
    def test_search_patient_by_partial_name_case_insensitive(self):
        self.assertEqual([p["id"] for p in sc.find_patients("RAHMAN")], ["P001"])

    def test_book_appointment_is_scheduled(self):
        a = sc.book_appointment("P001", "D01", "2026-10-05 09:00")
        self.assertEqual(a["status"], sc.STATUS_SCHEDULED)

    def test_duplicate_booking_rejected(self):
        sc.book_appointment("P001", "D01", "2026-10-05 09:00")
        with self.assertRaises(ValueError):
            sc.book_appointment("P002", "D01", "2026-10-05 09:00")

    def test_cancel_keeps_record_and_frees_slot(self):
        a = sc.book_appointment("P001", "D01", "2026-10-05 09:00")
        sc.cancel_appointment(a["id"])
        self.assertEqual(len(sc.appointments), 1)
        self.assertEqual(sc.appointments[0]["status"], sc.STATUS_CANCELLED)
        sc.book_appointment("P002", "D01", "2026-10-05 09:00")  # slot reusable

    # ---- unusual input -----------------------------------------------
    def test_unknown_patient_rejected(self):
        with self.assertRaises(ValueError):
            sc.book_appointment("P999", "D01", "2026-10-05 09:00")

    def test_blank_patient_name_rejected(self):
        with self.assertRaises(ValueError):
            sc.add_patient("P003", "")

    def test_known_limitation_free_text_time_is_accepted(self):
        """KNOWN LIMITATION (documented in AI card): 'tomorrow' is stored as-is."""
        a = sc.book_appointment("P001", "D01", "tomorrow")
        self.assertEqual(a["when"], "tomorrow")

    def test_known_limitation_equivalent_times_not_detected(self):
        """KNOWN LIMITATION: '09:00' and '9:00' are treated as different slots."""
        sc.book_appointment("P001", "D01", "2026-10-05 09:00")
        sc.book_appointment("P002", "D01", "2026-10-05 9:00")  # slips through

    def test_known_limitation_cancel_twice_is_silent(self):
        """KNOWN LIMITATION: cancelling an already cancelled appointment succeeds."""
        a = sc.book_appointment("P001", "D01", "2026-10-05 09:00")
        sc.cancel_appointment(a["id"])
        sc.cancel_appointment(a["id"])  # no error - will be fixed in Stage 2/4


if __name__ == "__main__":
    unittest.main(verbosity=2)
