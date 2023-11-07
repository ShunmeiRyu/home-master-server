from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="EMAIL_", strict=False, env_file_encoding="utf8"
    )
    HOST: str
    PORT: int
    ADDRESS: str
    PASSWORD: str


email_settings = Settings()