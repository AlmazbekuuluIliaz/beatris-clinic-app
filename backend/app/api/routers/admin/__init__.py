from __future__ import annotations

from fastapi import APIRouter, Depends

from app.api.deps import require_admin
from app.api.routers.admin.appointments import router as appointments_router
from app.api.routers.admin.clinic import router as clinic_router
from app.api.routers.admin.orders import router as orders_router
from app.api.routers.admin.products import router as products_router
from app.api.routers.admin.recommendations import router as recommendations_router
from app.api.routers.admin.reviews import router as reviews_router
from app.api.routers.admin.services import router as services_router
from app.api.routers.admin.settings import router as settings_router
from app.api.routers.admin.specialists import router as specialists_router
from app.api.routers.admin.users import router as users_router

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)

router.include_router(appointments_router)
router.include_router(clinic_router)
router.include_router(orders_router)
router.include_router(products_router)
router.include_router(recommendations_router)
router.include_router(reviews_router)
router.include_router(services_router)
router.include_router(settings_router)
router.include_router(specialists_router)
router.include_router(users_router)
