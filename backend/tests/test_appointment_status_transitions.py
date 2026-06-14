from app import models, repositories


def test_appointment_status_transition_from_pending_to_completed_is_not_allowed() -> None:
    assert not repositories.is_appointment_status_transition_allowed(
        models.AppointmentStatus.PENDING,
        models.AppointmentStatus.COMPLETED,
    )


def test_appointment_status_transition_from_pending_to_confirmed_is_allowed() -> None:
    assert repositories.is_appointment_status_transition_allowed(
        models.AppointmentStatus.PENDING,
        models.AppointmentStatus.CONFIRMED,
    )


def test_appointment_status_transition_from_confirmed_to_completed_is_allowed() -> None:
    assert repositories.is_appointment_status_transition_allowed(
        models.AppointmentStatus.CONFIRMED,
        models.AppointmentStatus.COMPLETED,
    )
