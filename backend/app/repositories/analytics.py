from __future__ import annotations

from datetime import date, datetime, timedelta

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app import models


def _paid_orders_filter():
    return or_(
        models.Order.payment_status == models.PaymentStatus.PAID,
        models.Order.order_status.in_(
            (
                models.OrderStatus.PAID,
                models.OrderStatus.PROCESSING,
                models.OrderStatus.DELIVERED,
            )
        ),
    )


def _period_to_str(value) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()[:10]
    return str(value)[:10]


def get_sales_analytics(
    db: Session,
    date_from: date,
    date_to: date,
    top_limit: int = 5,
) -> dict:
    paid_filter = _paid_orders_filter()
    period_start = datetime.combine(date_from, datetime.min.time())
    period_end = datetime.combine(date_to + timedelta(days=1), datetime.min.time())

    def with_period(statement: Select) -> Select:
        return (
            statement.where(paid_filter)
            .where(models.Order.created_at >= period_start)
            .where(models.Order.created_at < period_end)
        )

    kpi_row = db.execute(
        with_period(
            select(
                func.coalesce(func.sum(models.Order.total_price), 0),
                func.count(models.Order.id),
            )
        )
    ).one()
    revenue = float(kpi_row[0] or 0)
    orders_count = int(kpi_row[1] or 0)
    average_check = revenue / orders_count if orders_count else 0.0

    day_col = func.date(models.Order.created_at)
    period_rows = db.execute(
        with_period(
            select(
                day_col,
                func.coalesce(func.sum(models.Order.total_price), 0),
                func.count(models.Order.id),
            )
        )
        .group_by(day_col)
        .order_by(day_col)
    ).all()
    revenue_by_period = [
        {
            "period": _period_to_str(row[0]),
            "revenue": float(row[1] or 0),
            "ordersCount": int(row[2] or 0),
        }
        for row in period_rows
    ]

    top_rows = db.execute(
        with_period(
            select(
                models.OrderItem.product_title,
                func.coalesce(func.sum(models.OrderItem.quantity), 0),
                func.coalesce(func.sum(models.OrderItem.subtotal), 0),
            ).join(models.Order, models.OrderItem.order_id == models.Order.id)
        )
        .group_by(models.OrderItem.product_title)
        .order_by(func.sum(models.OrderItem.subtotal).desc())
        .limit(top_limit)
    ).all()
    top_products = [
        {
            "productTitle": row[0],
            "quantity": int(row[1] or 0),
            "revenue": float(row[2] or 0),
        }
        for row in top_rows
    ]

    return {
        "revenue": revenue,
        "ordersCount": orders_count,
        "averageCheck": average_check,
        "dateFrom": date_from,
        "dateTo": date_to,
        "revenueByPeriod": revenue_by_period,
        "topProducts": top_products,
    }


def get_services_analytics(
    db: Session,
    date_from: date,
    date_to: date,
    top_limit: int = 5,
) -> dict:
    """Аналитика приёмов по количеству (без денег — цены услуг пока не заданы).

    KPI по статусам считаются по всем записям периода. Динамика по дням и топ
    услуг — по завершённым приёмам. Группировка по дате приёма (appointment_date).
    """
    in_period = (
        models.Appointment.appointment_date >= date_from,
        models.Appointment.appointment_date <= date_to,
    )

    # --- KPI: распределение всех записей периода по статусам ---
    by_status = {status.value: 0 for status in models.AppointmentStatus}
    for status_value, count in db.execute(
        select(models.Appointment.status, func.count(models.Appointment.id))
        .where(*in_period)
        .group_by(models.Appointment.status)
    ).all():
        key = status_value.value if hasattr(status_value, "value") else str(status_value)
        by_status[key] = int(count or 0)
    total_appointments = sum(by_status.values())

    completed = (models.Appointment.status == models.AppointmentStatus.COMPLETED,)

    # --- Динамика: завершённые приёмы по дням ---
    day_col = models.Appointment.appointment_date
    period_rows = db.execute(
        select(day_col, func.count(models.Appointment.id))
        .where(*in_period, *completed)
        .group_by(day_col)
        .order_by(day_col)
    ).all()
    appointments_by_period = [
        {"period": _period_to_str(row[0]), "appointmentsCount": int(row[1] or 0)}
        for row in period_rows
    ]

    # --- Топ услуг по числу завершённых приёмов ---
    top_rows = db.execute(
        select(models.Service.title, func.count(models.Appointment.id))
        .join(models.Service, models.Appointment.service_id == models.Service.id)
        .where(*in_period, *completed)
        .group_by(models.Service.title)
        .order_by(func.count(models.Appointment.id).desc())
        .limit(top_limit)
    ).all()
    top_services = [
        {"serviceTitle": row[0], "appointmentsCount": int(row[1] or 0)}
        for row in top_rows
    ]

    return {
        "totalAppointments": total_appointments,
        "appointmentsByStatus": by_status,
        "dateFrom": date_from,
        "dateTo": date_to,
        "appointmentsByPeriod": appointments_by_period,
        "topServices": top_services,
    }


LOW_STOCK_THRESHOLD = 5


def _enum_key(value) -> str:
    return value.value if hasattr(value, "value") else str(value)


def admin_analytics(db: Session, period_days: int, reference_date: date) -> dict:
    today = reference_date
    period_start = today - timedelta(days=period_days - 1)

    appt_by_status = {status.value: 0 for status in models.AppointmentStatus}
    total_appointments = 0
    for status_value, count in db.execute(
        select(models.Appointment.status, func.count())
        .group_by(models.Appointment.status)
    ).all():
        appt_by_status[_enum_key(status_value)] = count
        total_appointments += count

    today_appointments = db.scalar(
        select(func.count())
        .select_from(models.Appointment)
        .where(models.Appointment.appointment_date == today)
    ) or 0

    period_appointments = db.scalar(
        select(func.count())
        .select_from(models.Appointment)
        .where(
            models.Appointment.appointment_date >= period_start,
            models.Appointment.appointment_date <= today,
        )
    ) or 0

    paid_filter = models.Order.payment_status == models.PaymentStatus.PAID
    total_paid = db.scalar(
        select(func.coalesce(func.sum(models.Order.total_price), 0)).where(paid_filter)
    ) or 0
    paid_orders = db.scalar(
        select(func.count()).select_from(models.Order).where(paid_filter)
    ) or 0
    period_revenue = db.scalar(
        select(func.coalesce(func.sum(models.Order.total_price), 0)).where(
            paid_filter,
            func.date(models.Order.created_at) >= period_start,
            func.date(models.Order.created_at) <= today,
        )
    ) or 0
    average_order_value = float(total_paid) / paid_orders if paid_orders else 0.0

    total_orders = db.scalar(select(func.count()).select_from(models.Order)) or 0
    orders_by_payment = {status.value: 0 for status in models.PaymentStatus}
    for status_value, count in db.execute(
        select(models.Order.payment_status, func.count())
        .group_by(models.Order.payment_status)
    ).all():
        orders_by_payment[_enum_key(status_value)] = count

    orders_by_status = {status.value: 0 for status in models.OrderStatus}
    for status_value, count in db.execute(
        select(models.Order.order_status, func.count())
        .group_by(models.Order.order_status)
    ).all():
        orders_by_status[_enum_key(status_value)] = count

    active_services = db.scalar(
        select(func.count()).select_from(models.Service).where(models.Service.is_active.is_(True))
    ) or 0
    active_products = db.scalar(
        select(func.count()).select_from(models.Product).where(models.Product.is_active.is_(True))
    ) or 0
    total_stock = db.scalar(
        select(func.coalesce(func.sum(models.Product.stock), 0)).where(models.Product.is_active.is_(True))
    ) or 0
    low_stock = db.scalar(
        select(func.count())
        .select_from(models.Product)
        .where(
            models.Product.is_active.is_(True),
            models.Product.stock < LOW_STOCK_THRESHOLD,
        )
    ) or 0

    in_period_appt = (
        models.Appointment.appointment_date >= period_start,
        models.Appointment.appointment_date <= today,
        models.Appointment.status != models.AppointmentStatus.CANCELLED,
    )
    top_services = [
        {"id": service_id, "title": title, "count": count}
        for service_id, title, count in db.execute(
            select(models.Service.id, models.Service.title, func.count(models.Appointment.id))
            .join(models.Appointment, models.Appointment.service_id == models.Service.id)
            .where(*in_period_appt)
            .group_by(models.Service.id, models.Service.title)
            .order_by(func.count(models.Appointment.id).desc())
            .limit(5)
        ).all()
    ]
    top_specialists = [
        {"id": specialist_id, "title": full_name, "count": count}
        for specialist_id, full_name, count in db.execute(
            select(models.Specialist.id, models.Specialist.full_name, func.count(models.Appointment.id))
            .join(models.Appointment, models.Appointment.specialist_id == models.Specialist.id)
            .where(*in_period_appt)
            .group_by(models.Specialist.id, models.Specialist.full_name)
            .order_by(func.count(models.Appointment.id).desc())
            .limit(5)
        ).all()
    ]

    return {
        "generatedAt": datetime.now(),
        "periodDays": period_days,
        "appointments": {
            "total": total_appointments,
            "today": today_appointments,
            "inPeriod": period_appointments,
            "byStatus": appt_by_status,
        },
        "revenue": {
            "totalPaid": float(total_paid),
            "inPeriod": float(period_revenue),
            "paidOrders": paid_orders,
            "averageOrderValue": round(average_order_value, 2),
        },
        "orders": {
            "total": total_orders,
            "byPaymentStatus": orders_by_payment,
            "byOrderStatus": orders_by_status,
        },
        "catalog": {
            "activeServices": active_services,
            "activeProducts": active_products,
            "totalStock": int(total_stock),
            "lowStock": low_stock,
        },
        "topServices": top_services,
        "topSpecialists": top_specialists,
    }
