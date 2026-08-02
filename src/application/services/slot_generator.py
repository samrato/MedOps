from datetime import UTC, date, datetime, timedelta

from src.application.dto.appointment_dto import TimeSlotDTO
from src.domain.entities.doctor import Doctor
from src.domain.value_objects.time_slot import TimeSlot


class SlotGenerator:
    """Generates continuous discrete time slots for a doctor on a specific date."""

    def generate_slots_for_date(
        self, doctor: Doctor, target_date: date, slot_duration_minutes: int | None = None
    ) -> list[TimeSlotDTO]:
        duration = slot_duration_minutes or doctor.slot_duration_minutes or 30

        # Check if target date is a holiday
        if any(h.date == target_date for h in doctor.holidays):
            return []

        day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday
        wh_list = [wh for wh in doctor.working_hours if wh.day_of_week == day_of_week and wh.is_active]
        if not wh_list:
            return []

        breaks_today = [b for b in doctor.breaks if b.day_of_week == day_of_week]

        slots: list[TimeSlotDTO] = []
        for wh in wh_list:
            current_start_dt = datetime.combine(target_date, wh.start_time, tzinfo=UTC)
            work_end_dt = datetime.combine(target_date, wh.end_time, tzinfo=UTC)

            while current_start_dt + timedelta(minutes=duration) <= work_end_dt:
                current_end_dt = current_start_dt + timedelta(minutes=duration)
                slot_candidate = TimeSlot(start_time=current_start_dt, end_time=current_end_dt)

                # Check break collision
                is_on_break = False
                for b in breaks_today:
                    break_start_dt = datetime.combine(target_date, b.start_time, tzinfo=UTC)
                    break_end_dt = datetime.combine(target_date, b.end_time, tzinfo=UTC)
                    break_slot = TimeSlot(start_time=break_start_dt, end_time=break_end_dt)
                    if slot_candidate.overlaps(break_slot):
                        is_on_break = True
                        break

                if not is_on_break:
                    slots.append(
                        TimeSlotDTO(
                            start_time=current_start_dt,
                            end_time=current_end_dt,
                            is_available=True,
                        )
                    )

                current_start_dt = current_end_dt

        return slots
