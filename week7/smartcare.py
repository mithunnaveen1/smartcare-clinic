"""SmartCare domain layer (v0.4)."""
from appointment import Appointment, AppointmentStatus
from clinic import Clinic
from exceptions import (DoubleBookingError, DuplicateIdError,
                         InvalidStatusTransitionError, SmartCareError,
                         UnknownEntityError)
from patient import Patient
from practitioner import Practitioner

__all__ = ["Appointment", "AppointmentStatus", "Clinic", "Patient", "Practitioner",
           "SmartCareError", "InvalidStatusTransitionError", "DoubleBookingError",
           "UnknownEntityError", "DuplicateIdError"]
