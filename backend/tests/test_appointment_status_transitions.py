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


def test_appointment_status_transition_from_pending_to_cancelled_is_allowed() -> None:
    assert repositories.is_appointment_status_transition_allowed(
        models.AppointmentStatus.PENDING,
        models.AppointmentStatus.CANCELLED,
    )


def test_appointment_status_transition_from_confirmed_to_completed_is_allowed() -> None:
    assert repositories.is_appointment_status_transition_allowed(
        models.AppointmentStatus.CONFIRMED,
        models.AppointmentStatus.COMPLETED,
    )


def test_appointment_status_transition_from_confirmed_to_cancelled_is_allowed() -> None:
    assert repositories.is_appointment_status_transition_allowed(
        models.AppointmentStatus.CONFIRMED,
        models.AppointmentStatus.CANCELLED,
    )


def test_appointment_status_transition_from_confirmed_to_pending_is_allowed() -> None:
    assert repositories.is_appointment_status_transition_allowed(
        models.AppointmentStatus.CONFIRMED,
        models.AppointmentStatus.PENDING,
    )


def test_appointment_status_transition_from_completed_to_pending_is_allowed() -> None:
    assert repositories.is_appointment_status_transition_allowed(
        models.AppointmentStatus.COMPLETED,
        models.AppointmentStatus.PENDING,
    )


def test_appointment_status_transition_from_cancelled_to_pending_is_allowed() -> None:
    assert repositories.is_appointment_status_transition_allowed(
        models.AppointmentStatus.CANCELLED,
        models.AppointmentStatus.PENDING,
    )


def test_appointment_status_transition_from_cancelled_to_confirmed_is_not_allowed() -> None:
    assert not repositories.is_appointment_status_transition_allowed(
        models.AppointmentStatus.CANCELLED,
        models.AppointmentStatus.CONFIRMED,
    )


def test_appointment_status_transition_from_cancelled_to_completed_is_not_allowed() -> None:
    assert not repositories.is_appointment_status_transition_allowed(
        models.AppointmentStatus.CANCELLED,
        models.AppointmentStatus.COMPLETED,
    )


def test_appointment_status_transition_from_completed_to_cancelled_is_not_allowed() -> None:
    assert not repositories.is_appointment_status_transition_allowed(
        models.AppointmentStatus.COMPLETED,
        models.AppointmentStatus.CANCELLED,
    )


def test_appointment_status_transition_from_pending_to_pending_is_allowed() -> None:
    assert repositories.is_appointment_status_transition_allowed(
        models.AppointmentStatus.PENDING,
        models.AppointmentStatus.PENDING,
    )
