import asyncio
from datetime import date, timedelta

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_concurrent_booking_race_condition(async_client: AsyncClient, seeded_entities: dict):
    doctor = seeded_entities["doctor"]
    patient = seeded_entities["patient"]
    patient_token = seeded_entities["patient_token"]

    headers = {"Authorization": f"Bearer {patient_token}"}

    today = date.today()
    days_ahead = 7 - today.weekday() if today.weekday() != 0 else 7
    target_date = today + timedelta(days=days_ahead)

    avail_resp = await async_client.get(
        f"/api/v1/doctors/{doctor.id}/availability?date={target_date.isoformat()}"
    )
    first_slot = avail_resp.json()["data"]["slots"][0]

    book_payload = {
        "doctor_id": str(doctor.id),
        "patient_id": str(patient.id),
        "start_time": first_slot["start_time"],
        "end_time": first_slot["end_time"],
        "reason": "Concurrent Test",
    }

    # Simulate 5 concurrent booking requests for the exact same slot
    tasks = [
        async_client.post("/api/v1/appointments", json=book_payload, headers=headers)
        for _ in range(5)
    ]
    responses = await asyncio.gather(*tasks)

    status_codes = [r.status_code for r in responses]
    success_count = status_codes.count(201)
    conflict_count = status_codes.count(409)

    # Exactly ONE booking must succeed, and all others must fail with 409 Conflict
    assert success_count == 1
    assert conflict_count == 4
