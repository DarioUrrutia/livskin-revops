"""Configuración del ERP Flask. Lee env vars con Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    erp_db_user: str = "erp_user"
    erp_db_password: str
    erp_db_name: str = "livskin_erp"
    erp_db_host: str = "postgres-data"
    erp_db_port: int = 5432

    flask_secret_key: str
    flask_env: str = "production"

    session_duration_hours: int = 48
    session_inactivity_hours: int = 2
    login_max_attempts: int = 8
    login_lockout_minutes: int = 15

    log_level: str = "INFO"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.erp_db_user}:{self.erp_db_password}"
            f"@{self.erp_db_host}:{self.erp_db_port}/{self.erp_db_name}"
        )


settings = Settings()  # type: ignore[call-arg]
