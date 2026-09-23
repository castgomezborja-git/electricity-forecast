import requests

from electricity_forecast.config import settings


AEMET_API_BASE_URL="https://opendata.aemet.es/opendata/api/prediccion/especifica/municipio/horaria"
AEMET_ESTACION_ID = "3182Y"

def _get_prediccion_url(municipio_id: str, api_key: str) -> str:
    """Llama al endpoint de predicción horaria, y del JSON de respuesta extrae el campo datos (la URL donde está el contenido real)"""

    url = f"{AEMET_API_BASE_URL}/{municipio_id}"
    
    response = requests.get(url, headers={"api_key": api_key})

    response.raise_for_status()

    response.encoding = 'ISO-8859-1'
    json_response = response.json()

    return json_response['datos']


def fetch_hourly_forecast(municipio_id: str, api_key: str) -> dict:
    prediction_url = _get_prediccion_url(municipio_id, api_key)

    response = requests.get(prediction_url)
    response.raise_for_status()
    
    response.encoding = 'ISO-8859-1'
    return response.json()