from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_LINK: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    TOKEN_EXPIRE: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()