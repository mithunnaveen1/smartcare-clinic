"""Machine-readable copy of the APPROVED v0.4 UML (see Stage 4 workbook, section 5).

Changes from v0.3 (all justified in the workbook):
  * exceptions DuplicateIdError, UnknownEntityError, DoubleBookingError added
    under SmartCareError (implementation needed distinct, catchable errors);
  * Clinic.book_appointment no longer takes appointment_id (Clinic generates IDs,
    so callers cannot create duplicate IDs);
  * Clinic.cancel_appointment / complete_appointment added (status change is
    still decided by Appointment).
"""

UML_V04 = {
    "AppointmentStatus": {"members": ["SCHEDULED", "COMPLETED", "CANCELLED"]},
    "SmartCareError": {"exception": True},
    "InvalidStatusTransitionError": {"exception": True},
    "DoubleBookingError": {"exception": True},
    "UnknownEntityError": {"exception": True},
    "DuplicateIdError": {"exception": True},
    "Patient": {
        "attributes": ["patient_id", "name", "date_of_birth", "phone"],
        "operations": {"matches": ["text"]},
    },
    "Practitioner": {
        "attributes": ["practitioner_id", "name", "specialty"],
        "operations": {},
    },
    "Appointment": {
        "attributes": ["appointment_id", "patient", "practitioner", "start", "status", "is_active"],
        "operations": {"cancel": [], "complete": []},
    },
    "Clinic": {
        "attributes": [],
        "operations": {
            "register_patient": ["patient"],
            "register_practitioner": ["practitioner"],
            "search_patients": ["text"],
            "book_appointment": ["patient_id", "practitioner_id", "start"],
            "cancel_appointment": ["appointment_id"],
            "complete_appointment": ["appointment_id"],
            "schedule_for": ["practitioner_id"],
            "history_for": ["patient_id"],
            "status_report": [],
        },
    },
}
