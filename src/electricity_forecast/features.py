import numpy as np
import pandas as pd


def _add_price_lag(df: pd.DataFrame, hour: int) -> pd.DataFrame:
    fechas_lag = df.index - pd.Timedelta(hour, 'hours')
    df["precio_lag_hours_" + str(hour)] = df["price_eur_mwh"].reindex(fechas_lag).values

    return df


def add_price_lags(df: pd.DataFrame, list_hours: list[int]) -> pd.DataFrame:
    df_lag = df.copy()

    for hour in list_hours:
        df_lag = _add_price_lag(df_lag, hour)


    return df_lag


def add_cyclical_hour(df: pd.DataFrame) -> pd.DataFrame:
    df_cyclical = df.copy()
    hora = df_cyclical.index.hour + df_cyclical.index.minute / 60
    df_cyclical["hora_sin"] = np.sin(2 * np.pi * hora / 24)
    df_cyclical["hora_cos"] = np.cos(2 * np.pi * hora / 24)

    return df_cyclical


def add_cyclical_dayofweek(df: pd.DataFrame) -> pd.DataFrame:
    df_cyclical_day = df.copy()
    day = df_cyclical_day.index.weekday
    df_cyclical_day["day_sin"] = np.sin(2 * np.pi * day / 7)
    df_cyclical_day["day_cos"] = np.cos(2 * np.pi * day / 7)

    return df_cyclical_day