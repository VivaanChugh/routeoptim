"""Application configuration."""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # OSRM Configuration
    osrm_base_url: str = "http://router.project-osrm.org"
    osrm_cache_ttl: int = 3600  # 1 hour
    osrm_profile: str = "driving"  # driving, walking, cycling
    osrm_timeout: int = 30  # seconds

    # OR-Tools Configuration
    or_tools_time_limit: int = 30  # seconds
    or_tools_verbose: bool = False

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = False

    # Database Configuration
    database_url: str = "postgresql+asyncpg://user:password@localhost:5432/routeoptim"
    database_enabled: bool = False

    # API Configuration
    api_v1_prefix: str = "/api/v1"
    cors_origins: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
    ]
    max_stops: int = 25
    max_vehicles: int = 5
    min_stops: int = 2

    # Application
    environment: str = "development"
    debug: bool = True
    app_name: str = "Last-Mile Route Optimizer"
    app_version: str = "1.0.0"

    # Optimization Defaults
    default_vehicle_capacity: int = 100
    default_service_time_minutes: int = 5
    default_max_route_duration_minutes: int = 480  # 8 hours


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
