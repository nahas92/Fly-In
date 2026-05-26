"""Drone model representing a single drone in the simulation."""

from typing import Optional
from models.zone import Zone


class Drone:
    """A single drone being routed through the graph.

    Tracks current position, in-transit state, and delivery status.

    Attributes:
        drone_id: Unique integer identifier.
        current_zone: The zone this drone currently occupies.
        delivered: Whether this drone has reached the end zone.
        in_transit_to: Zone this drone is mid-flight toward.
        turns_in_transit: Turns spent on current restricted move.
    """
    def __init__(self, drone_id: int, start_zone: Zone) -> None:
        """Initialize a Drone at the start zone.

        Args:
            drone_id: Unique identifier (1-indexed).
            start_zone: The zone where this drone begins.
        """
        self.drone_id: int = drone_id
        self.current_zone: Zone = start_zone
        self.delivered: bool = False
        self.in_transit_to: Optional[Zone] = None
        self.turns_in_transit: int = 0

    def label(self) -> str:
        """Return the drone's display label (e.g. 'D1').

        Returns:
            String in the format D<id>.
        """
        return f"D{self.drone_id}"

    def is_in_transit(self) -> bool:
        """Check if this drone is mid-flight to a restricted zone.

        Returns:
            True if the drone is currently in transit.
        """
        return self.in_transit_to is not None

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            String showing drone label and current zone name.
        """
        return (
            f"Drone({self.label()}, "
            f"at={self.current_zone.name!r})"
        )
