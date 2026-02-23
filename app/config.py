from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_LINK: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()