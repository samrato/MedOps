from src.domain.events.appointment_events import (
    AppointmentBookedEvent,
    AppointmentCancelledEvent,
    AppointmentRescheduledEvent,
)
from src.infrastructure.logging.logger import logger


class NotificationService:
    async def send_booking_confirmation(self, event: AppointmentBookedEvent) -> None:
        logger.info(
            "Sending booking notification",
            appointment_id=str(event.appointment_id),
            patient_id=str(event.patient_id),
            doctor_id=str(event.doctor_id),
            start_time=event.start_time.isoformat(),
        )

    async def send_cancellation_notice(self, event: AppointmentCancelledEvent) -> None:
        logger.info(
            "Sending cancellation notification",
            appointment_id=str(event.appointment_id),
            patient_id=str(event.patient_id),
            reason=event.reason,
        )

    async def send_reschedule_notice(self, event: AppointmentRescheduledEvent) -> None:
        logger.info(
            "Sending reschedule notification",
            appointment_id=str(event.appointment_id),
            patient_id=str(event.patient_id),
            new_start_time=event.new_start_time.isoformat(),
        )
