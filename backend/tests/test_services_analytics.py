"""Проверка аналитики услуг: в выручку идут только завершённые приёмы."""

from datetime import date, time
from decimal import Decimal

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app import models, repositories


@pytest.fixture()
def db() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    models.Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def _make_appointment(
    session: Session,
    *,
    service: models.Service,
    specialist: models.Specialist,
    appt_date: date,
    appt_time: time,
    status: models.AppointmentStatus,
) -> None:
    session.add(
        models.Appointment(
            patient_name="Пациент",
            patient_phone="+70000000000",
            service_id=service.id,
            specialist_id=specialist.id,
            appointment_date=appt_date,
            appointment_time=appt_time,
            status=status,
        )
    )


@pytest.fixture()
def catalog(db: Session) -> dict:
    category = models.ServiceCategory(title="Косметология", slug="cosmetology")
    db.add(category)
    db.flush()
    laser = models.Service(
        category_id=category.id, title="Лазер", slug="laser",
        description="-", price=Decimal("9000"),
    )
    peeling = models.Service(
        category_id=category.id, title="Пилинг", slug="peeling",
        description="-", price=Decimal("3000"),
    )
    specialist = models.Specialist(
        full_name="Врач", position="Косметолог", specialization="Косметология",
    )
    db.add_all([laser, peeling, specialist])
    db.flush()
    return {"laser": laser, "peeling": peeling, "specialist": specialist}


def test_services_analytics_counts_only_completed(db: Session, catalog: dict) -> None:
    laser, peeling, spec = catalog["laser"], catalog["peeling"], catalog["specialist"]
    inside = date(2026, 6, 10)
    outside = date(2026, 1, 1)
    done = models.AppointmentStatus.COMPLETED

    # Учитываются: два завершённых лазера и один пилинг в пределах периода
    _make_appointment(db, service=laser, specialist=spec, appt_date=inside, appt_time=time(10, 0), status=done)
    _make_appointment(db, service=laser, specialist=spec, appt_date=inside, appt_time=time(11, 0), status=done)
    _make_appointment(db, service=peeling, specialist=spec, appt_date=inside, appt_time=time(12, 0), status=done)
    # Не учитываются: незавершённый (confirmed) и завершённый вне периода
    _make_appointment(db, service=laser, specialist=spec, appt_date=inside, appt_time=time(13, 0),
                      status=models.AppointmentStatus.CONFIRMED)
    _make_appointment(db, service=peeling, specialist=spec, appt_date=outside, appt_time=time(10, 0), status=done)
    db.commit()

    result = repositories.get_services_analytics(db, date(2026, 6, 1), date(2026, 6, 30))

    # KPI по статусам: все записи периода (3 завершённых + 1 подтверждённый)
    assert result["totalAppointments"] == 4
    assert result["appointmentsByStatus"]["completed"] == 3
    assert result["appointmentsByStatus"]["confirmed"] == 1
    assert result["appointmentsByStatus"]["cancelled"] == 0
    assert result["appointmentsByStatus"]["pending"] == 0

    # Динамика и топ — по завершённым приёмам
    assert {"period": "2026-06-10", "appointmentsCount": 3} in result["appointmentsByPeriod"]

    titles = {s["serviceTitle"]: s for s in result["topServices"]}
    assert set(titles) == {"Лазер", "Пилинг"}
    assert titles["Лазер"]["appointmentsCount"] == 2
    assert titles["Пилинг"]["appointmentsCount"] == 1
    # Топ отсортирован по числу приёмов убыванию
    assert [s["serviceTitle"] for s in result["topServices"]] == ["Лазер", "Пилинг"]
    # Денег в ответе больше нет
    assert "revenue" not in result
    assert "averageCheck" not in result


def test_services_analytics_empty_period_is_safe(db: Session) -> None:
    result = repositories.get_services_analytics(db, date(2026, 6, 1), date(2026, 6, 30))
    assert result["totalAppointments"] == 0
    assert result["appointmentsByStatus"] == {
        "pending": 0, "confirmed": 0, "completed": 0, "cancelled": 0,
    }
    assert result["appointmentsByPeriod"] == []
    assert result["topServices"] == []
