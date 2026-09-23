from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, Numeric, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class WeatherRecordModel(Base):
    __tablename__ = "weather_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    is_real: Mapped[bool]
    weather_day: Mapped[date] = mapped_column(Date())
    ingested_at: Mapped[datetime]
    temperature: Mapped[Decimal | None]  = mapped_column(Numeric(5, 2), nullable=True)
    wind: Mapped[Decimal | None]  = mapped_column(Numeric(5, 2), nullable=True)
    precipitation: Mapped[Decimal | None]  = mapped_column(Numeric(5, 2), nullable=True)

    __table_args__ = (UniqueConstraint('weather_day', 'is_real', name='_weatherDay_isReal_uc'),)

    def __repr__(self) -> str:
        return f"WeatherRecord(id={self.id!r}, is_real={self.is_real!r}, weather_day={self.weather_day!r}, ingested_at={self.ingested_at!r}, temperature={self.temperature!r}, wind={self.wind!r}, precipitation={self.precipitation!r})"