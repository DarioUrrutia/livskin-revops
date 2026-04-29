"""Configuración del ERP Flask. Lee env vars con Pydantic Settings.

Durante MVP/dev usamos postgres superuser (ya configurado en postgres-data/.env).
Pre-cutover (Fase 6): crear rol erp_user con permisos limitados (ADR-0026).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    erp_db_user: str = "postgres"
    postgres_superuser_password: str
    erp_db_name: str = "livskin_erp"
    erp_db_host: str = "postgres-data"
    erp_db_port: int = 5432

    flask_secret_key: str = "dev-only-change-in-production"
    flask_env: str = "production"

    session_duration_hours: int = 48
    session_inactivity_hours: int = 2
    login_max_attempts: int = 8
    login_lockout_minutes: int = 15

    log_level: str = "INFO"

    # Cross-VPS: shared secret para endpoints internos (CI/CD, sensors, cron).
    # Pre-Bloque-0 default insecure — rotar en producción a valor random.
    audit_internal_token: str = "change-me-in-production"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.erp_db_user}:{self.postgres_superuser_password}"
            f"@{self.erp_db_host}:{self.erp_db_port}/{self.erp_db_name}"
        )


settings = Settings()  # type: ignore[call-arg]
