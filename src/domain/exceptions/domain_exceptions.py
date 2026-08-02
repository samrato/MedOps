"""
Domain Exceptions for MedOps.
Pure domain error definitions with status codes and explicit message structures.
"""

class DomainException(Exception):
    """Base exception for all domain errors."""
    code: str = "DOMAIN_ERROR"
    status_code: int = 400

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class SlotAlreadyBookedException(DomainException):
    code = "SLOT_ALREADY_BOOKED"
    status_code = 409

    def __init__(self, message: str = "Selected slot has already been booked."):
        super().__init__(message)


class DoubleBookingException(DomainException):
    code = "DOUBLE_BOOKING_CONSTRAINED"
    status_code = 409

    def __init__(self, message: str = "Patient already has an overlapping appointment."):
        super().__init__(message)


class PastAppointmentException(DomainException):
    code = "PAST_APPOINTMENT_NOT_ALLOWED"
    status_code = 400

    def __init__(self, message: str = "Appointments cannot be booked in the past."):
        super().__init__(message)


class OutsideWorkingHoursException(DomainException):
    code = "OUTSIDE_WORKING_HOURS"
    status_code = 400

    def __init__(self, message: str = "Selected slot is outside doctor's working hours."):
        super().__init__(message)


class DoctorOnHolidayException(DomainException):
    code = "DOCTOR_ON_HOLIDAY"
    status_code = 400

    def __init__(self, message: str = "Doctor is on holiday during the requested slot."):
        super().__init__(message)


class DoctorOnBreakException(DomainException):
    code = "DOCTOR_ON_BREAK"
    status_code = 400

    def __init__(self, message: str = "Requested slot falls within doctor's break time."):
        super().__init__(message)


class AppointmentNotFoundException(DomainException):
    code = "APPOINTMENT_NOT_FOUND"
    status_code = 404

    def __init__(self, message: str = "Appointment not found."):
        super().__init__(message)


class DoctorNotFoundException(DomainException):
    code = "DOCTOR_NOT_FOUND"
    status_code = 404

    def __init__(self, message: str = "Doctor not found."):
        super().__init__(message)


class PatientNotFoundException(DomainException):
    code = "PATIENT_NOT_FOUND"
    status_code = 404

    def __init__(self, message: str = "Patient not found."):
        super().__init__(message)


class InvalidAppointmentStateException(DomainException):
    code = "INVALID_APPOINTMENT_STATE"
    status_code = 422

    def __init__(self, message: str = "Operation invalid for current appointment state."):
        super().__init__(message)


class UnauthorizedException(DomainException):
    code = "UNAUTHORIZED"
    status_code = 401

    def __init__(self, message: str = "Authentication failed or token invalid."):
        super().__init__(message)


class ForbiddenException(DomainException):
    code = "FORBIDDEN"
    status_code = 403

    def __init__(self, message: str = "You do not have permission to perform this action."):
        super().__init__(message)
