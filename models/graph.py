"""Graph model holding all zones and connections."""

from typing import List, Optional
from models.zone import Zone
from models.connection import Connection


class Graph:
    """The complete routing network of zones and connections.

    Built by the parser from a map file.
    Used by the simulation and pathfinding algorithm.

    Attributes:
        zones: All zones keyed by name for fast lookup.
        connections: All connections in the graph.
        start_zone: The zone all drones begin in.
        end_zone: The zone all drones must reach.
        nb_drones: Total number of drones to route.
    """
    def __init__(self) -> None:
        """Initialize an empty Graph."""
        self.zones: dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.start_zone: Optional[Zone] = None
        self.end_zone: Optional[Zone] = None
        self.nb_drones: int = 0

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph.

        Args:
            zone: The zone to add.

        Raises:
            ValueError: If a zone with this name already exists.
        """
        if zone.name in self.zones:
            raise ValueError(
                f"Duplicate zone name: '{zone.name}'"
            )
        self.zones[zone.name] = zone

    def get_zone(self, name: str) -> Optional[Zone]:
        """Look up a zone by name.

        Args:
            name: The zone name to look up.

        Returns:
            The Zone if found, None otherwise.
        """
        return self.zones.get(name)

    def add_connection(self, connection: Connection) -> None:
        """Add a connection to the graph.

        Args:
            connection: The connection to add.

        Raises:
            ValueError: If this connection already exists.
        """
        a = connection.zone_a.name
        b = connection.zone_b.name
        for existing in self.connections:
            if existing.connects(a, b):
                raise ValueError(
                    f"Duplicate connection: '{a}-{b}'"
                )
        self.connections.append(connection)

    def get_neighbors(self, zone_name: str) -> List[Zone]:
        """Get all zones directly reachable from a given zone.

        Args:
            zone_name: The name of the zone to check from.

        Returns:
            List of all zones connected to this one.
        """
        neighbors: List[Zone] = []
        for conn in self.connections:
            if (
                conn.zone_a.name == zone_name
                or conn.zone_b.name == zone_name
            ):
                neighbor = conn.other_zone(zone_name)
                neighbors.append(neighbor)
        return neighbors

    def get_connection(
        self, zone_name_1: str, zone_name_2: str
    ) -> Optional[Connection]:
        """Find the connection between two zones by name.

        Args:
            zone_name_1: Name of one zone.
            zone_name_2: Name of the other zone.

        Returns:
            The Connection if it exists, None otherwise.
        """
        for conn in self.connections:
            if conn.connects(zone_name_1, zone_name_2):
                return conn
        return None

    def __repr__(self) -> str:
        """Return a developer-friendly string representation.

        Returns:
            String showing zone and connection counts.
        """
        return (
            f"Graph({len(self.zones)} zones, "
            f"{len(self.connections)} connections)"
        )
