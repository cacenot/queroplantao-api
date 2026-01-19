"""Coordinate value object for geographic location."""

from decimal import Decimal
from typing import Optional

from pydantic import Field, field_validator


class Coordinate:
    """
    Coordinate value object representing latitude and longitude.

    Used for storing geographic location with proper precision and validation.
    Latitude range: -90 to +90 degrees
    Longitude range: -180 to +180 degrees
    """

    latitude: Optional[Decimal] = Field(
        default=None,
        ge=-90,
        le=90,
        max_digits=10,
        decimal_places=8,
        description="Latitude coordinate (-90 to +90)",
    )
    longitude: Optional[Decimal] = Field(
        default=None,
        ge=-180,
        le=180,
        max_digits=11,
        decimal_places=8,
        description="Longitude coordinate (-180 to +180)",
    )

    def __init__(
        self,
        latitude: Optional[Decimal] = None,
        longitude: Optional[Decimal] = None,
    ):
        """Initialize coordinate with latitude and longitude."""
        self.latitude = latitude
        self.longitude = longitude

    @field_validator("latitude", "longitude", mode="before")
    @classmethod
    def validate_coordinate(
        cls, value: Optional[Decimal | float | str]
    ) -> Optional[Decimal]:
        """Convert coordinate value to Decimal."""
        if value is None:
            return None
        if isinstance(value, Decimal):
            return value
        return Decimal(str(value))

    @property
    def is_valid(self) -> bool:
        """Check if both latitude and longitude are set."""
        return self.latitude is not None and self.longitude is not None

    def __str__(self) -> str:
        """String representation of the coordinate."""
        if not self.is_valid:
            return "Coordinate(not set)"
        return f"Coordinate({self.latitude}, {self.longitude})"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Coordinate(latitude={self.latitude}, longitude={self.longitude})"
