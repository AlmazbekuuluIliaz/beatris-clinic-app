from __future__ import annotations

from fastapi import HTTPException, status


def raise_bad_request(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def raise_not_found(detail: str = "Не найдено") -> None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def raise_conflict(detail: str) -> None:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


APPOINTMENT_ERRORS = {
    "service_not_found": "Услуга не найдена",
    "specialist_not_found": "Специалист не найден",
    "specialist_does_not_provide_service": "Специалист не оказывает выбранную услугу",
    "slot_unavailable": "Выбранное время недоступно",
    "slot_taken": "Выбранное время уже занято",
    "invalid_date": "Некорректная дата",
}

APPOINTMENT_RESCHEDULE_ERRORS = {
    "specialist_not_found": "Специалист не найден",
    "specialist_does_not_provide_service": "Специалист не оказывает услугу этой записи",
    "slot_unavailable": "Выбранное время недоступно",
    "slot_taken": "Выбранное время уже занято",
}

ORDER_ERRORS = {
    "user_not_found": "Пользователь не найден",
    "product_not_found": "Товар не найден или неактивен",
    "could_not_create_order": "Не удалось создать заказ",
}

USER_ERRORS = {
    "phone_exists": "Пользователь с таким телефоном уже существует",
    "email_exists": "Пользователь с таким email уже существует",
    "integrity_error": "Пользователь с такими данными уже существует",
}
