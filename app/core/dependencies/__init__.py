"""Dependencies module - FastAPI dependency injection."""

from app.core.dependencies.database import SessionDep, get_session
from app.core.dependencies.settings import SettingsDep, get_settings


__all__ = ["SessionDep", "SettingsDep", "get_session", "get_settings"]

