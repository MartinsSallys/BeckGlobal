from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = 'Backend Boilerplate'
    debug: bool = False
    database_url: str = 'postgresql+psycopg://usuario:senha@localhost:5432/beckglobal'
    secret_key: str = ''
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 30
    cors_origins: list[str] = ['*']

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


settings = Settings()
