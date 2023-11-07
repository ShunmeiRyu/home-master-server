from pydantic_settings import BaseSettings, SettingsConfigDict
from hashlib import sha256
from os import urandom


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="UTF8", env_prefix="AUTH_", strict=False
    )

    ALGORITHM: str = "HS256"
    SECRETS_KEY: str = sha256(urandom(1024)).hexdigest()
    ACCESS_TOKEN_EXP_HOURS: int = 2


auth_settings = Settings()
