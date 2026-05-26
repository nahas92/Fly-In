"""Zone model representing a node in the drone routing graph."""

from enum import Enum
from typing import Optional


class ZoneType(Enum):
    """Enumeration of all valid zone types."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone:
    """A single node in the routing graph.

    Attributes:
        name: Unique identifier for this zone.
        x: X coordinate on the map.
        y: Y coordinate on the map.
        zone_type: The movement cost/accessibility type.
        color: Optional display color for visualization.
        max_drones: Maximum drones allowed simultaneously.
        current_drones: How many drones are here right now.
    """

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: ZoneType = ZoneType.NORMAL,
        color: Optional[str] = None,
        max_drones: int = 1,
    ) -> None:
        """Initialize a Zone.

        Args:
            name: Unique zone identifier.
            x: X coordinate.
            y: Y coordinate.
            zone_type: Type affecting movement cost.
            color: Optional color string for visualization.
            max_drones: Max drones allowed at once (default 1).
        """
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: ZoneType = zone_type
        self.color: Optional[str] = color
        self.max_drones: int = max_drones
        self.current_drones: int = 0

    def is_full(self) -> bool:
        """Check whether this zone has reached its drone capacity.

        Returns:
            True if current drones equals or exceeds max capacity.
        """
        return self.current_drones >= self.max_drones

    def can_accept_drone(self) -> bool:
        """Check if this zone can accept one more drone.

        Blocked zones can never accept drones regardless of capacity.

        Returns:
            True if the zone is not blocked and not full.
        """
        if self.zone_type == ZoneType.BLOCKED:
            return False
        return not self.is_full()

    def add_drone(self) -> None:
        """Increment the drone count for this zone."""
        self.current_drones += 1

    def remove_drone(self) -> None:
        """Decrement the drone count for this zone."""
        if self.current_drones > 0:
            self.current_drones -= 1

    def movement_cost(self) -> int:
        """Return the turn cost to move INTO this zone.

        Returns:
            2 for restricted zones, 1 for all others.
        """
        if self.zone_type == ZoneType.RESTRICTED:
            return 2
        return 1

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            String showing zone name and type.
        """
        return f"Zone({self.name!r}, {self.zone_type.value})"
