from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from electricity_forecast.models import WeatherRecordModel
from electricity_forecast.schemas import WeatherRecord


def load_weather_records(records: list[WeatherRecord], session: Session) -> None:
    """Inserta datos del clima, actualizando el valor si ya existe."""
    for record in records:
        stmt = insert(WeatherRecordModel).values(
            is_real = record.is_real,
            weather_day = record.weather_day,
            ingested_at = record.ingested_at,
            temperature = record.temperature,
            wind = record.wind,
            precipitation = record.precipitation
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["weather_day", "is_real"],
            set_={
                "ingested_at": stmt.excluded.ingested_at,
                "temperature": stmt.excluded.temperature,
                "wind": stmt.excluded.wind,
                "precipitation": stmt.excluded.precipitation
            },
        )
        session.execute(stmt)
    session.commit()
