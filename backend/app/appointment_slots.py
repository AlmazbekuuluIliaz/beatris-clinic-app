from datetime import date, datetime, time

from sqlalchemy.orm import Session

from app import models
from app import repositories


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def parse_time(value: str) -> time:
    return datetime.strptime(value, "%H:%M").time()


def minutes_from_time(value: time) -> int:
    return value.hour * 60 + value.minute


def time_from_minutes(value: int) -> str:
    return f"{value // 60:02d}:{value % 60:02d}"


def intervals_overlap(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return left[0] < right[1] and right[0] < left[1]


def appointment_interval(appointment: models.Appointment) -> tuple[int, int]:
    duration = appointment.service.duration_minutes or 30
    start = minutes_from_time(appointment.appointment_time)
    return start, start + duration


def available_slots(
    db: Session,
    specialist_id: str,
    service: models.Service,
    schedule_date: date,
) -> list[dict]:
    duration = service.duration_minutes or 30
    busy_intervals = [
        appointment_interval(appointment)
        for appointment in repositories.list_busy_appointments(db, specialist_id, schedule_date)
    ]
    result: list[dict] = []

    for schedule_item in repositories.list_schedule_items(db, specialist_id, schedule_date):
        cursor = minutes_from_time(schedule_item.start_time)
        schedule_end = minutes_from_time(schedule_item.end_time)

        while cursor + duration <= schedule_end:
            candidate = (cursor, cursor + duration)
            if not any(intervals_overlap(candidate, busy) for busy in busy_intervals):
                result.append(
                    {
                        "specialistId": specialist_id,
                        "date": schedule_date.isoformat(),
                        "time": time_from_minutes(cursor),
                    }
                )
            cursor += duration

    return result
