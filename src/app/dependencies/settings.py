"""Settings dependency for FastAPI injection."""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends

from src.app.config import Settings


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
