"""Dependencies module - FastAPI dependency injection."""

from src.app.dependencies.database import SessionDep, get_session
from src.app.dependencies.settings import SettingsDep, get_settings


__all__ = ["SessionDep", "SettingsDep", "get_session", "get_settings"]

