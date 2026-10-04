"""Machine-readable copy of the approved v0.3 UML (used by check_consistency.py).

Format: class -> {"attributes": [...public names...], "operations": {name: [param names]}}
Private members (leading underscore in the UML as '-') are not checked here.
"""
from datetime import date, datetime

UML_V03 = {
    "AppointmentStatus": {"members": ["SCHEDULED", "COMPLETED", "CANCELLED"]},
    "InvalidStatusTransitionError": {"exception": True},
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
            "book_appointment": ["appointment_id", "patient_id", "practitioner_id", "start"],
            "schedule_for": ["practitioner_id"],
            "history_for": ["patient_id"],
            "status_report": [],
        },
    },
}
