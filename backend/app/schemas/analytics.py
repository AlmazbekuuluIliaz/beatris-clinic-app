from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class SalesPeriodPoint(BaseModel):
    period: str
    revenue: float
    ordersCount: int


class TopProductPoint(BaseModel):
    productTitle: str
    quantity: int
    revenue: float


class SalesAnalyticsResponse(BaseModel):
    revenue: float
    ordersCount: int
    averageCheck: float
    dateFrom: date
    dateTo: date
    revenueByPeriod: list[SalesPeriodPoint]
    topProducts: list[TopProductPoint]


class AppointmentsByStatus(BaseModel):
    pending: int
    confirmed: int
    completed: int
    cancelled: int


class ServicesPeriodPoint(BaseModel):
    period: str
    appointmentsCount: int


class TopServicePoint(BaseModel):
    serviceTitle: str
    appointmentsCount: int


class ServicesAnalyticsResponse(BaseModel):
    """Аналитика приёмов по количеству (без денег — цены услуг пока не заданы)."""

    totalAppointments: int
    appointmentsByStatus: AppointmentsByStatus
    dateFrom: date
    dateTo: date
    appointmentsByPeriod: list[ServicesPeriodPoint]
    topServices: list[TopServicePoint]
