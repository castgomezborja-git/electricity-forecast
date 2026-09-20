from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    aemet_api_key: str
    aemet_municipio_id: str
    database_url: str



settings = Settings()