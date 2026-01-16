"""Shifts module routes."""

from fastapi import APIRouter

router = APIRouter(prefix="/shifts", tags=["Shifts"])


# TODO: Add shift endpoints
# @router.get("/")
# @router.get("/{shift_id}")
# @router.post("/")
# @router.put("/{shift_id}")
# @router.delete("/{shift_id}")
# @router.post("/{shift_id}/assign")
# @router.post("/{shift_id}/unassign")
