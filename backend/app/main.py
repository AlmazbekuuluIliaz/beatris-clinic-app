from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles

from app.api.routers import api_router

OPENAPI_TAGS = [
    {"name": "Clinic", "description": "Публичная информация о клинике"},
    {"name": "Auth", "description": "Регистрация, авторизация и обновление токена доступа"},
    {"name": "Users", "description": "Профиль пользователя"},
    {"name": "Services", "description": "Услуги медицинского центра"},
    {"name": "Specialists", "description": "Специалисты медицинского центра"},
    {"name": "Appointments", "description": "Онлайн-запись на приём"},
    {"name": "Products", "description": "Товары интернет-магазина"},
    {"name": "Wishlist", "description": "Избранные товары пользователя"},
    {"name": "Cart", "description": "Корзина пользователя"},
    {"name": "Orders", "description": "Заказы и оплата"},
    {"name": "Recommendations", "description": "Рекомендации врача"},
    {"name": "Doctor", "description": "Функции врача"},
    {"name": "Admin", "description": "Управление данными в административной панели"},
    {"name": "Health", "description": "Проверки работоспособности сервиса (вне контракта)"},
]

app = FastAPI(
    title="Beatris API",
    version="1.0.0",
    description="API веб-приложения медицинского центра эстетической медицины Beatris",
    openapi_tags=OPENAPI_TAGS,
    servers=[{"url": "/", "description": "Хост сервиса (пути уже включают префикс /api/v1)"}],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")


@app.get("/", include_in_schema=False)
def root_redirect():
    return RedirectResponse(url="/admin")


# Статику админки отдаём без кэширования, чтобы правки сразу подхватывались браузером.
_NO_CACHE = {"Cache-Control": "no-store"}


@app.get("/admin", response_class=HTMLResponse, include_in_schema=False)
@app.get("/admin.html", response_class=HTMLResponse, include_in_schema=False)
def serve_admin_html():
    with open("admin.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), headers=_NO_CACHE)


@app.get("/admin.js", include_in_schema=False)
def serve_admin_js():
    with open("admin.js", "r", encoding="utf-8") as f:
        return Response(content=f.read(), media_type="application/javascript", headers=_NO_CACHE)


@app.get("/admin-config.js", include_in_schema=False)
def serve_admin_config_js():
    with open("admin-config.js", "r", encoding="utf-8") as f:
        return Response(content=f.read(), media_type="application/javascript", headers=_NO_CACHE)


@app.get("/admin.css", include_in_schema=False)
def serve_admin_css():
    with open("admin.css", "r", encoding="utf-8") as f:
        return Response(content=f.read(), media_type="text/css", headers=_NO_CACHE)
