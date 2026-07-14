from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Backend Boilerplate"
    limit: int = 100
    database_url: str
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()  # cria uma instância da classe Settings, que carrega as configurações do arquivo .env e permite o acesso a elas em outras partes do aplicativo.
