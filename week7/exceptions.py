"""Domain exceptions for SmartCare (v0.4)."""


class SmartCareError(Exception):
    """Base class for all SmartCare domain errors."""


class InvalidStatusTransitionError(SmartCareError):
    """An appointment status change that the lifecycle does not allow (FR-10)."""


class DoubleBookingError(SmartCareError):
    """The practitioner already has an active appointment at that time (FR-06)."""


class UnknownEntityError(SmartCareError):
    """A patient, practitioner or appointment ID is not registered (FR-07)."""


class DuplicateIdError(SmartCareError):
    """An ID is already registered (NFR-01 data integrity)."""
