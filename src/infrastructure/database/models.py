import uuid
from datetime import UTC, date, datetime, time

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.value_objects.appointment_status import AppointmentStatus
from src.domain.value_objects.user_role import UserRole
from src.infrastructure.database.base import Base


class UserModel(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, native_enum=False), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    doctor_profile: Mapped["DoctorModel | None"] = relationship("DoctorModel", back_populates="user", uselist=False)
    patient_profile: Mapped["PatientModel | None"] = relationship("PatientModel", back_populates="user", uselist=False)


class DoctorModel(Base):
    __tablename__ = "doctors"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    specialty: Mapped[str] = mapped_column(String(100), nullable=False)
    bio: Mapped[str] = mapped_column(Text, default="", nullable=False)
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    user: Mapped[UserModel] = relationship("UserModel", back_populates="doctor_profile")
    working_hours: Mapped[list["WorkingHoursModel"]] = relationship(
        "WorkingHoursModel", back_populates="doctor", cascade="all, delete-orphan"
    )
    holidays: Mapped[list["HolidayModel"]] = relationship(
        "HolidayModel", back_populates="doctor", cascade="all, delete-orphan"
    )
    breaks: Mapped[list["BreakTimeModel"]] = relationship(
        "BreakTimeModel", back_populates="doctor", cascade="all, delete-orphan"
    )
    appointments: Mapped[list["AppointmentModel"]] = relationship("AppointmentModel", back_populates="doctor")


class WorkingHoursModel(Base):
    __tablename__ = "working_hours"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    slot_duration_minutes: Mapped[int] = mapped_column(Integer, default=30, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    doctor: Mapped[DoctorModel] = relationship("DoctorModel", back_populates="working_hours")

    __table_args__ = (
        UniqueConstraint("doctor_id", "day_of_week", name="uq_doctor_working_hours_day"),
    )


class HolidayModel(Base):
    __tablename__ = "holidays"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), default="", nullable=False)

    doctor: Mapped[DoctorModel] = relationship("DoctorModel", back_populates="holidays")

    __table_args__ = (
        UniqueConstraint("doctor_id", "date", name="uq_doctor_holiday_date"),
    )


class BreakTimeModel(Base):
    __tablename__ = "break_times"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False, index=True
    )
    day_of_week: Mapped[int] = mapped_column(Integer, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    description: Mapped[str] = mapped_column(String(255), default="Lunch Break", nullable=False)

    doctor: Mapped[DoctorModel] = relationship("DoctorModel", back_populates="breaks")


class PatientModel(Base):
    __tablename__ = "patients"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    phone_number: Mapped[str] = mapped_column(String(50), default="", nullable=False)
    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    medical_history_summary: Mapped[str] = mapped_column(Text, default="", nullable=False)

    user: Mapped[UserModel] = relationship("UserModel", back_populates="patient_profile")
    appointments: Mapped[list["AppointmentModel"]] = relationship("AppointmentModel", back_populates="patient")


class AppointmentModel(Base):
    __tablename__ = "appointments"

    doctor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("doctors.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("patients.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    status: Mapped[AppointmentStatus] = mapped_column(
        SQLEnum(AppointmentStatus, native_enum=False), default=AppointmentStatus.SCHEDULED, nullable=False, index=True
    )
    reason: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    notes: Mapped[str] = mapped_column(Text, default="", nullable=False)

    doctor: Mapped[DoctorModel] = relationship("DoctorModel", back_populates="appointments")
    patient: Mapped[PatientModel] = relationship("PatientModel", back_populates="appointments")

    __table_args__ = (
        Index("idx_doctor_time_status", "doctor_id", "start_time", "end_time", "status"),
        Index("idx_patient_time_status", "patient_id", "start_time", "end_time", "status"),
        UniqueConstraint("doctor_id", "start_time", name="uq_doctor_appointment_slot"),
    )


class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    actor_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    entity_name: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    details: Mapped[str] = mapped_column(Text, default="", nullable=False)
    ip_address: Mapped[str] = mapped_column(String(45), default="", nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False, index=True
    )
