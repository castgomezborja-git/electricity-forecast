from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from electricity_forecast.schemas import WeatherRecord

MADRID_TZ = ZoneInfo("Europe/Madrid")
hoy = datetime.now(tz=MADRID_TZ).date()


def _parse_decimal_5_2(value) -> Decimal | None:
    if value is None or value == "":
        return None

    if isinstance(value, Decimal):
        return value.quantize(Decimal("0.01"))

    text = str(value).strip()
    text = text.replace(".", "").replace(",", ".")
    return Decimal(text).quantize(Decimal("0.01"))


def parse_weather_records(raw_data: dict, is_real: bool) -> list[WeatherRecord]:
    weather_records = []
    for item in raw_data:
        wdate = date.fromisoformat(item['fecha'])
        record = WeatherRecord(
            is_real=is_real,
            weather_day=wdate,
            ingested_at=datetime.now(tz=MADRID_TZ),
            temperature=_parse_decimal_5_2(item.get("tmed", None)),
            wind=_parse_decimal_5_2(item.get("velmedia", None)),
            precipitation=Decimal("0.00") if item.get("prec", None) == "Ip" else _parse_decimal_5_2(item.get("prec", None)),
        )
        weather_records.append(record)
    return weather_records
    