from datetime import date, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_appointment_lifecycle_and_validation(async_client: AsyncClient, seeded_entities: dict):
    doctor = seeded_entities["doctor"]
    patient = seeded_entities["patient"]
    patient_token = seeded_entities["patient_token"]

    headers = {"Authorization": f"Bearer {patient_token}"}

    # 1. Get Availability
    # Pick next Monday for guaranteed working hours
    today = date.today()
    days_ahead = 7 - today.weekday() if today.weekday() != 0 else 7
    target_date = today + timedelta(days=days_ahead)

    avail_resp = await async_client.get(
        f"/api/v1/doctors/{doctor.id}/availability?date={target_date.isoformat()}"
    )
    assert avail_resp.status_code == 200
    avail_data = avail_resp.json()
    assert avail_data["success"] is True
    assert len(avail_data["data"]["slots"]) > 0

    first_slot = avail_data["data"]["slots"][0]
    start_time = first_slot["start_time"]
    end_time = first_slot["end_time"]

    # 2. Book Appointment
    book_payload = {
        "doctor_id": str(doctor.id),
        "patient_id": str(patient.id),
        "start_time": start_time,
        "end_time": end_time,
        "reason": "Consultation",
    }
    book_resp = await async_client.post("/api/v1/appointments", json=book_payload, headers=headers)
    assert book_resp.status_code == 201
    book_data = book_resp.json()
    assert book_data["success"] is True
    appointment_id = book_data["data"]["id"]

    # 3. Attempt Double Booking Same Slot -> Expect 409 SLOT_ALREADY_BOOKED
    double_resp = await async_client.post("/api/v1/appointments", json=book_payload, headers=headers)
    assert double_resp.status_code == 409
    double_data = double_resp.json()
    assert double_data["success"] is False
    assert double_data["error"]["code"] == "SLOT_ALREADY_BOOKED"

    # 4. Get Patient Appointments
    patient_apps_resp = await async_client.get(
        f"/api/v1/patients/{patient.id}/appointments", headers=headers
    )
    assert patient_apps_resp.status_code == 200
    assert len(patient_apps_resp.json()["data"]) >= 1

    # 5. Reschedule Appointment
    second_slot = avail_data["data"]["slots"][1]
    reschedule_payload = {
        "new_start_time": second_slot["start_time"],
        "new_end_time": second_slot["end_time"],
    }
    resched_resp = await async_client.patch(
        f"/api/v1/appointments/{appointment_id}/reschedule", json=reschedule_payload, headers=headers
    )
    assert resched_resp.status_code == 200
    assert resched_resp.json()["data"]["status"] == "RESCHEDULED"

    # 6. Cancel Appointment
    cancel_payload = {"reason": "No longer needed"}
    cancel_resp = await async_client.patch(
        f"/api/v1/appointments/{appointment_id}/cancel", json=cancel_payload, headers=headers
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["data"]["status"] == "CANCELLED"
