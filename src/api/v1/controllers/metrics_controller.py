from fastapi import APIRouter, Response
from prometheus_client import generate_latest

router = APIRouter(tags=["Metrics"])


@router.get("/metrics")
async def metrics():
    """Endpoint for Prometheus metric scraper."""
    data = generate_latest()
    return Response(content=data, media_type="text/plain; version=0.0.4; charset=utf-8")
