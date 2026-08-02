import uuid
from datetime import date, time

from src.application.services.slot_generator import SlotGenerator
from src.domain.entities.break_time import BreakTime
from src.domain.entities.doctor import Doctor
from src.domain.entities.holiday import Holiday
from src.domain.entities.working_hours import WorkingHours


def test_generate_slots_normal_day():
    generator = SlotGenerator()
    doctor_id = uuid.uuid4()
    # Monday = 0
    target_date = date(2026, 8, 10)  # Monday

    doctor = Doctor(
        id=doctor_id,
        user_id=uuid.uuid4(),
        specialty="General",
        slot_duration_minutes=30,
        working_hours=[
            WorkingHours(
                id=uuid.uuid4(),
                doctor_id=doctor_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(11, 0),
            )
        ],
    )

    slots = generator.generate_slots_for_date(doctor, target_date)
    # 9:00 to 11:00 with 30 min slots = 4 slots
    assert len(slots) == 4
    assert slots[0].start_time.hour == 9 and slots[0].start_time.minute == 0
    assert slots[3].start_time.hour == 10 and slots[3].start_time.minute == 30


def test_generate_slots_with_break():
    generator = SlotGenerator()
    doctor_id = uuid.uuid4()
    target_date = date(2026, 8, 10)  # Monday

    doctor = Doctor(
        id=doctor_id,
        user_id=uuid.uuid4(),
        specialty="General",
        slot_duration_minutes=30,
        working_hours=[
            WorkingHours(
                id=uuid.uuid4(),
                doctor_id=doctor_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(12, 0),
            )
        ],
        breaks=[
            BreakTime(
                id=uuid.uuid4(),
                doctor_id=doctor_id,
                day_of_week=0,
                start_time=time(10, 0),
                end_time=time(11, 0),
                description="Tea break",
            )
        ],
    )

    slots = generator.generate_slots_for_date(doctor, target_date)
    # Total slots without break = 6. 10:00-10:30 and 10:30-11:00 excluded. Total = 4.
    assert len(slots) == 4


def test_generate_slots_on_holiday():
    generator = SlotGenerator()
    doctor_id = uuid.uuid4()
    target_date = date(2026, 8, 10)

    doctor = Doctor(
        id=doctor_id,
        user_id=uuid.uuid4(),
        specialty="General",
        slot_duration_minutes=30,
        working_hours=[
            WorkingHours(
                id=uuid.uuid4(),
                doctor_id=doctor_id,
                day_of_week=0,
                start_time=time(9, 0),
                end_time=time(17, 0),
            )
        ],
        holidays=[
            Holiday(id=uuid.uuid4(), doctor_id=doctor_id, date=target_date, description="National Holiday")
        ],
    )

    slots = generator.generate_slots_for_date(doctor, target_date)
    assert len(slots) == 0
