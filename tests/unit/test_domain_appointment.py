import uuid
from datetime import UTC, datetime, timedelta

import pytest

from src.domain.entities.appointment import Appointment
from src.domain.exceptions.domain_exceptions import InvalidAppointmentStateException
from src.domain.value_objects.appointment_status import AppointmentStatus
from src.domain.value_objects.time_slot import TimeSlot


def test_time_slot_overlap():
    now = datetime.now(UTC)
    slot1 = TimeSlot(start_time=now, end_time=now + timedelta(minutes=30))
    slot2 = TimeSlot(start_time=now + timedelta(minutes=15), end_time=now + timedelta(minutes=45))
    slot3 = TimeSlot(start_time=now + timedelta(minutes=30), end_time=now + timedelta(minutes=60))

    assert slot1.overlaps(slot2) is True
    assert slot1.overlaps(slot3) is False  # Touch boundaries, not overlapping


def test_appointment_reschedule_and_cancel():
    now = datetime.now(UTC) + timedelta(days=1)
    app = Appointment(
        id=uuid.uuid4(),
        doctor_id=uuid.uuid4(),
        patient_id=uuid.uuid4(),
        start_time=now,
        end_time=now + timedelta(minutes=30),
    )

    assert app.status == AppointmentStatus.SCHEDULED

    # Reschedule
    new_start = now + timedelta(hours=2)
    new_end = new_start + timedelta(minutes=30)
    app.reschedule(new_start, new_end)
    assert app.status == AppointmentStatus.RESCHEDULED
    assert app.start_time == new_start

    # Cancel
    app.cancel(reason="Patient request")
    assert app.status == AppointmentStatus.CANCELLED
    assert "Patient request" in app.notes

    # Attempting to cancel already cancelled appointment raises exception
    with pytest.raises(InvalidAppointmentStateException):
        app.cancel()
