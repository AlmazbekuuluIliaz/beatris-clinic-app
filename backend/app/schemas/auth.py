from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

from app.schemas.users import User


class RegisterRequest(BaseModel):
    fullName: str
    phone: str
    email: str | None = None
    password: str = Field(min_length=8)
    role: Literal["patient", "doctor"] = "patient"
    position: str | None = Field(default=None, max_length=255)
    specialization: str | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def validate_doctor_fields(self):
        if self.role == "doctor":
            if not self.position:
                raise ValueError("Для регистрации врача поле position обязательно")
            if not self.specialization:
                raise ValueError("Для регистрации врача поле specialization обязательно")
        return self


class LoginRequest(BaseModel):
    phone: str
    password: str
    remember: bool = True


class SpecialistProfile(BaseModel):
    specialistId: str
    position: str
    specialization: str
    experienceYears: int | None = None


class AuthResponse(BaseModel):
    accessToken: str
    tokenType: str = "Bearer"
    expiresIn: int
    role: str
    user: User
    specialistProfile: SpecialistProfile | None = None


class RefreshTokenResponse(BaseModel):
    accessToken: str
    tokenType: str = "Bearer"
    expiresIn: int
