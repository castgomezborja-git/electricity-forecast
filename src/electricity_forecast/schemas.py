from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class WeatherRecord(BaseModel):
    is_real: bool
    weather_day: date
    ingested_at: datetime
    temperature: Decimal | None
    wind: Decimal | None
    precipitation: Decimal | None
