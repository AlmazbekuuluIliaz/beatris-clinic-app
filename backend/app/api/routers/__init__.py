from __future__ import annotations

from fastapi import APIRouter

from app.api.routers import (
    admin,
    appointments,
    auth,
    cart,
    clinic,
    doctor,
    orders,
    products,
    recommendations,
    reviews,
    services,
    specialists,
    users,
    wishlist,
)

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(auth.admin_router)
api_router.include_router(admin.router)
api_router.include_router(clinic.router)
api_router.include_router(services.router)
api_router.include_router(specialists.router)
api_router.include_router(appointments.router)
api_router.include_router(products.router)
api_router.include_router(reviews.router)
api_router.include_router(users.router)
api_router.include_router(wishlist.router)
api_router.include_router(cart.router)
api_router.include_router(orders.router)
api_router.include_router(recommendations.router)
api_router.include_router(doctor.router)
