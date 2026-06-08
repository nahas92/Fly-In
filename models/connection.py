"""Connection model representing an edge between two zones."""

from models.zone import Zone


class Connection:
    """A bidirectional link between two zones in the graph.

    Connections define valid movement paths for drones.
    They can have a capacity limit on simultaneous traversals.

    Attributes:
        zone_a: First zone endpoint.
        zone_b: Second zone endpoint.
        max_link_capacity: Max drones traversing at once.
        current_usage: How many drones are using this link now.
    """

    def __init__(
        self,
        zone_a: Zone,
        zone_b: Zone,
        max_link_capacity: int = 1,
    ) -> None:
        """Initialize a Connection.

        Args:
            zone_a: One endpoint of this connection.
            zone_b: The other endpoint.
            max_link_capacity: Max simultaneous traversals (default 1).
        """
        self.zone_a: Zone = zone_a
        self.zone_b: Zone = zone_b
        self.max_link_capacity: int = max_link_capacity
        self.current_usage: int = 0

    def connects(self, zone_name_1: str, zone_name_2: str) -> bool:
        """Check if this connection links two zones by name.

        Order does not matter since connections are bidirectional.

        Args:
            zone_name_1: Name of one zone.
            zone_name_2: Name of the other zone.

        Returns:
            True if this connection links these two zones.
        """
        a = self.zone_a.name
        b = self.zone_b.name
        return (
            (a == zone_name_1 and b == zone_name_2)
            or (a == zone_name_2 and b == zone_name_1)
        )

    def other_zone(self, zone_name: str) -> Zone:
        """Given one zone name, return the zone on the other end.

        Args:
            zone_name: Name of the known zone.

        Returns:
            The zone on the opposite end of this connection.

        Raises:
            ValueError: If zone_name is not an endpoint here.
        """
        if self.zone_a.name == zone_name:
            return self.zone_b
        if self.zone_b.name == zone_name:
            return self.zone_a
        raise ValueError(
            f"Zone '{zone_name}' is not part of this connection."
        )

    def is_at_capacity(self) -> bool:
        """Check if this connection is fully occupied.

        Returns:
            True if current usage equals max link capacity.
        """
        return self.current_usage >= self.max_link_capacity

    def add_usage(self) -> None:
        """Register one drone traversing this connection."""
        self.current_usage += 1

    def remove_usage(self) -> None:
        """Unregister one drone from traversing this connection."""
        if self.current_usage > 0:
            self.current_usage -= 1

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            String showing both zone names.
        """
        return (
            f"Connection({self.zone_a.name!r}"
            f" <-> {self.zone_b.name!r})"
        )
