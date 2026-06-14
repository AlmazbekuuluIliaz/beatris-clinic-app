from sqlalchemy import UniqueConstraint

from app import models


def test_active_appointment_slot_constraint_uses_generated_marker() -> None:
    constraint = next(
        item
        for item in models.Appointment.__table__.constraints
        if isinstance(item, UniqueConstraint)
        and item.name == "uq_appointments_active_specialist_slot"
    )

    assert [column.name for column in constraint.columns] == [
        "specialist_id",
        "appointment_date",
        "appointment_time",
        "active_slot_marker",
    ]
    assert models.Appointment.__table__.c.active_slot_marker.computed is not None
