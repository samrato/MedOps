from fastapi import APIRouter

from src.api.v1.controllers.admin_controller import router as admin_router
from src.api.v1.controllers.appointments_controller import router as appointments_router
from src.api.v1.controllers.auth_controller import router as auth_router
from src.api.v1.controllers.doctors_controller import router as doctors_router
from src.api.v1.controllers.health_controller import router as health_router
from src.api.v1.controllers.metrics_controller import router as metrics_router
from src.api.v1.controllers.patients_controller import router as patients_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(doctors_router)
api_v1_router.include_router(patients_router)
api_v1_router.include_router(appointments_router)
api_v1_router.include_router(admin_router)

root_router = APIRouter()
root_router.include_router(health_router)
root_router.include_router(metrics_router)
root_router.include_router(api_v1_router)
