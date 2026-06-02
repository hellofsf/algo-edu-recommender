"""Configuration management using Pydantic Settings."""

from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+asyncpg://algoedu:algoedu_pass@localhost:5432/algo_edu"

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j_password"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_private_key_path: str = "/app/secrets/jwt-private.pem"
    jwt_public_key_path: str = "/app/secrets/jwt-public.pem"
    jwt_algorithm: str = "RS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    # App
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def jwt_private_key(self) -> str | None:
        """Load JWT private key from file."""
        path = Path(self.jwt_private_key_path)
        if path.exists():
            return path.read_text()
        return None

    @property
    def jwt_public_key(self) -> str | None:
        """Load JWT public key from file."""
        path = Path(self.jwt_public_key_path)
        if path.exists():
            return path.read_text()
        return None


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
