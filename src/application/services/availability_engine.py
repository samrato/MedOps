import uuid
from datetime import UTC, date, datetime

from src.application.dto.appointment_dto import DoctorAvailabilityDTO, TimeSlotDTO
from src.application.services.slot_generator import SlotGenerator
from src.domain.exceptions.domain_exceptions import DoctorNotFoundException
from src.domain.repositories.appointment_repository import AppointmentRepository
from src.domain.repositories.doctor_repository import DoctorRepository
from src.domain.value_objects.time_slot import TimeSlot
from src.infrastructure.cache.redis_client import RedisCache, redis_cache


class AvailabilityEngine:
    def __init__(
        self,
        doctor_repo: DoctorRepository,
        appointment_repo: AppointmentRepository,
        cache: RedisCache = redis_cache,
    ) -> None:
        self._doctor_repo = doctor_repo
        self._appointment_repo = appointment_repo
        self._slot_generator = SlotGenerator()
        self._cache = cache

    async def get_doctor_availability(
        self, doctor_id: uuid.UUID, target_date: date
    ) -> DoctorAvailabilityDTO:
        cache_key = f"availability:{doctor_id}:{target_date.isoformat()}"
        cached_data = await self._cache.get_json(cache_key)
        if cached_data:
            slots = [
                TimeSlotDTO(
                    start_time=datetime.fromisoformat(s["start_time"]),
                    end_time=datetime.fromisoformat(s["end_time"]),
                    is_available=s["is_available"],
                    reason_unavailable=s.get("reason_unavailable"),
                )
                for s in cached_data["slots"]
            ]
            return DoctorAvailabilityDTO(
                doctor_id=doctor_id,
                date=target_date.isoformat(),
                slot_duration_minutes=cached_data["slot_duration_minutes"],
                slots=slots,
            )

        doctor = await self._doctor_repo.get_by_id(doctor_id)
        if not doctor:
            raise DoctorNotFoundException(f"Doctor with ID {doctor_id} not found.")

        # Generate standard potential slots for this day
        candidate_slots = self._slot_generator.generate_slots_for_date(doctor, target_date)

        # Fetch existing active appointments for doctor on target date
        day_start = datetime.combine(target_date, datetime.min.time(), tzinfo=UTC)
        day_end = datetime.combine(target_date, datetime.max.time(), tzinfo=UTC)
        booked_appointments = await self._appointment_repo.get_by_doctor(
            doctor_id, start_date=day_start, end_date=day_end
        )

        active_booked_slots = [
            TimeSlot(start_time=app.start_time, end_time=app.end_time)
            for app in booked_appointments
            if app.status.is_active()
        ]

        # Annotate slot availability
        final_slots: list[TimeSlotDTO] = []
        now = datetime.now(UTC)

        for slot_dto in candidate_slots:
            slot_vo = TimeSlot(start_time=slot_dto.start_time, end_time=slot_dto.end_time)
            
            # Check if in past
            if slot_vo.is_in_past(now):
                final_slots.append(
                    TimeSlotDTO(
                        start_time=slot_dto.start_time,
                        end_time=slot_dto.end_time,
                        is_available=False,
                        reason_unavailable="Slot is in the past",
                    )
                )
                continue

            # Check if occupied
            is_occupied = any(slot_vo.overlaps(booked) for booked in active_booked_slots)
            if is_occupied:
                final_slots.append(
                    TimeSlotDTO(
                        start_time=slot_dto.start_time,
                        end_time=slot_dto.end_time,
                        is_available=False,
                        reason_unavailable="SLOT_ALREADY_BOOKED",
                    )
                )
            else:
                final_slots.append(
                    TimeSlotDTO(
                        start_time=slot_dto.start_time,
                        end_time=slot_dto.end_time,
                        is_available=True,
                    )
                )

        availability_dto = DoctorAvailabilityDTO(
            doctor_id=doctor_id,
            date=target_date.isoformat(),
            slot_duration_minutes=doctor.slot_duration_minutes,
            slots=final_slots,
        )

        # Cache for 60 seconds
        cache_payload = {
            "doctor_id": str(doctor_id),
            "date": target_date.isoformat(),
            "slot_duration_minutes": doctor.slot_duration_minutes,
            "slots": [
                {
                    "start_time": s.start_time.isoformat(),
                    "end_time": s.end_time.isoformat(),
                    "is_available": s.is_available,
                    "reason_unavailable": s.reason_unavailable,
                }
                for s in final_slots
            ],
        }
        await self._cache.set_json(cache_key, cache_payload, ttl_seconds=60)

        return availability_dto
