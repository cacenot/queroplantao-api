"""Screening module API routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/screening", tags=["screening"])

# TODO: Implement endpoints for:
# - Template management (CRUD)
# - Process management (create, list, get, update status)
# - Step management (update step data, submit step)
# - Document review (review individual documents)
# - Token-based access for professionals
