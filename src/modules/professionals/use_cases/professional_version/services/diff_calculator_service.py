"""Service for calculating diffs between professional snapshots.

Compares two snapshots and generates ProfessionalChangeDiff entries
for each field-level change detected.
"""

from typing import Any
from uuid import UUID

from src.modules.professionals.domain.models.professional_change_diff import (
    ProfessionalChangeDiff,
)
from src.modules.professionals.domain.models.version_snapshot import (
    ProfessionalDataSnapshot,
)
from src.modules.screening.domain.models.enums import ChangeType


class DiffCalculatorService:
    """
    Service for calculating diffs between professional data snapshots.

    Generates granular field-level diffs that can be stored in
    ProfessionalChangeDiff for audit and visualization.
    """

    def calculate_diffs(
        self,
        version_id: UUID,
        organization_id: UUID,
        old_snapshot: ProfessionalDataSnapshot | None,
        new_snapshot: ProfessionalDataSnapshot,
    ) -> list[ProfessionalChangeDiff]:
        """
        Calculate diffs between two snapshots.

        Args:
            version_id: The version ID these diffs belong to.
            old_snapshot: Previous snapshot (None for new professional).
            new_snapshot: New snapshot being applied.

        Returns:
            List of ProfessionalChangeDiff entries.
        """
        diffs: list[ProfessionalChangeDiff] = []

        old = old_snapshot or {}

        # Compare personal_info
        if "personal_info" in new_snapshot:
            self._compare_objects(
                version_id=version_id,
                organization_id=organization_id,
                path="personal_info",
                old_obj=old.get("personal_info", {}),
                new_obj=new_snapshot["personal_info"],
                diffs=diffs,
            )

        # Compare collections (qualifications, companies, bank_accounts)
        for collection_name in ["qualifications", "companies", "bank_accounts"]:
            if collection_name in new_snapshot:
                self._compare_collections(
                    version_id=version_id,
                    organization_id=organization_id,
                    path=collection_name,
                    old_items=old.get(collection_name, []),
                    new_items=new_snapshot[collection_name],
                    diffs=diffs,
                )

        return diffs

    def _compare_objects(
        self,
        version_id: UUID,
        organization_id: UUID,
        path: str,
        old_obj: dict[str, Any],
        new_obj: dict[str, Any],
        diffs: list[ProfessionalChangeDiff],
    ) -> None:
        """Compare two objects and add diffs for changed fields."""
        all_keys = set(old_obj.keys()) | set(new_obj.keys())

        for key in all_keys:
            field_path = f"{path}.{key}"
            old_value = old_obj.get(key)
            new_value = new_obj.get(key)

            # Skip nested collections - they are handled separately
            if isinstance(new_value, list) or isinstance(old_value, list):
                if key in ["specialties", "educations"]:
                    # These are nested in qualifications
                    continue

            if old_value != new_value:
                if old_value is None and new_value is not None:
                    change_type = ChangeType.ADDED
                elif old_value is not None and new_value is None:
                    change_type = ChangeType.REMOVED
                else:
                    change_type = ChangeType.MODIFIED

                diffs.append(
                    ProfessionalChangeDiff(
                        organization_id=organization_id,
                        version_id=version_id,
                        field_path=field_path,
                        change_type=change_type,
                        old_value=old_value,
                        new_value=new_value,
                    )
                )

    def _compare_collections(
        self,
        version_id: UUID,
        organization_id: UUID,
        path: str,
        old_items: list[dict[str, Any]],
        new_items: list[dict[str, Any]],
        diffs: list[ProfessionalChangeDiff],
    ) -> None:
        """Compare two collections and add diffs."""
        # Build maps by ID for matching
        old_by_id: dict[str, dict[str, Any]] = {}
        for item in old_items:
            if item_id := item.get("id"):
                old_by_id[str(item_id)] = item

        new_by_id: dict[str, dict[str, Any]] = {}
        for idx, item in enumerate(new_items):
            item_id = item.get("id")
            if item_id:
                new_by_id[str(item_id)] = item
            else:
                # New item without ID - track by index
                new_by_id[f"new_{idx}"] = item

        # Find removed items
        for item_id, old_item in old_by_id.items():
            if item_id not in new_by_id:
                diffs.append(
                    ProfessionalChangeDiff(
                        organization_id=organization_id,
                        version_id=version_id,
                        field_path=f"{path}[id={item_id}]",
                        change_type=ChangeType.REMOVED,
                        old_value=old_item,
                        new_value=None,
                    )
                )

        # Find added and modified items
        for idx, new_item in enumerate(new_items):
            item_id = new_item.get("id")

            if item_id and str(item_id) in old_by_id:
                # Existing item - compare fields
                old_item = old_by_id[str(item_id)]
                item_path = f"{path}[id={item_id}]"

                # Compare object fields
                self._compare_objects(
                    version_id=version_id,
                    organization_id=organization_id,
                    path=item_path,
                    old_obj=old_item,
                    new_obj=new_item,
                    diffs=diffs,
                )

                # Handle nested collections (for qualifications)
                if path == "qualifications":
                    for nested_name in ["specialties", "educations"]:
                        if nested_name in new_item:
                            self._compare_collections(
                                version_id=version_id,
                                organization_id=organization_id,
                                path=f"{item_path}.{nested_name}",
                                old_items=old_item.get(nested_name, []),
                                new_items=new_item.get(nested_name, []),
                                diffs=diffs,
                            )
            else:
                # New item
                diffs.append(
                    ProfessionalChangeDiff(
                        organization_id=organization_id,
                        version_id=version_id,
                        field_path=f"{path}[{idx}]",
                        change_type=ChangeType.ADDED,
                        old_value=None,
                        new_value=new_item,
                    )
                )
