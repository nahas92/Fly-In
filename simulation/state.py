"""Simulation state tracking current positions and occupancy."""

from typing import List, Dict
from models.drone import Drone
from models.graph import Graph


class SimulationState:
    """Snapshot of the simulation at a given turn.

    Tracks drone positions, zone occupancy, connection usage,
    and in-transit drones. Does not make movement decisions.

    Attributes:
        graph: The routing graph for this simulation.
        drones: All drones being simulated.
        turn: The current turn number.
    """

    def __init__(self, graph: Graph, drones: List[Drone]) -> None:
        """Initialize simulation state with all drones at start.

        Args:
            graph: The routing graph.
            drones: All drones to simulate.
        """
        self.graph: Graph = graph
        self.drones: List[Drone] = drones
        self.turn: int = 0

    def get_zone_drone_count(self, zone_name: str) -> int:
        """Count how many active drones are currently in a zone.

        Does not count delivered drones or drones in transit.

        Args:
            zone_name: Name of the zone to check.

        Returns:
            Number of drones currently in this zone.
        """
        count = 0
        for drone in self.drones:
            if drone.delivered:
                continue
            if drone.is_in_transit():
                continue
            if drone.current_zone.name == zone_name:
                count += 1
        return count

    def get_connection_usage(
        self, zone_a_name: str, zone_b_name: str
    ) -> int:
        """Count how many drones are currently in transit
        on a specific connection.

        Args:
            zone_a_name: One end of the connection.
            zone_b_name: Other end of the connection.

        Returns:
            Number of drones currently using this connection.
        """
        count = 0
        for drone in self.drones:
            if not drone.is_in_transit():
                continue
            if drone.delivered:
                continue
            if drone.in_transit_to is None:
                continue
            conn = self.graph.get_connection(
                drone.current_zone.name,
                drone.in_transit_to.name
            )
            if conn is not None and conn.connects(
                zone_a_name, zone_b_name
            ):
                count += 1
        return count

    def get_active_drones(self) -> List[Drone]:
        """Return all drones that have not yet been delivered.

        Returns:
            List of drones still being routed.
        """
        return [d for d in self.drones if not d.delivered]

    def all_delivered(self) -> bool:
        """Check whether every drone has reached the end zone.

        Returns:
            True if all drones are delivered.
        """
        return all(d.delivered for d in self.drones)

    def zone_has_capacity(
        self,
        zone_name: str,
        planned_exits: Dict[str, int],
        planned_entries: Dict[str, int],
    ) -> bool:
        """Check if a zone can accept one more drone this turn.

        Takes planned exits into account so drones leaving
        a zone free up capacity for drones entering it
        on the same turn.

        Args:
            zone_name: Name of the zone to check.
            planned_exits: Dict of zone_name to number of
                drones planned to leave that zone this turn.

        Returns:
            True if the zone can accept one more drone.
        """
        zone = self.graph.get_zone(zone_name)
        if zone is None:
            return False

        current = self.get_zone_drone_count(zone_name)
        exits = planned_exits.get(zone_name, 0)
        entries = planned_entries.get(zone_name, 0)
        effective = current - exits + entries

        return effective < zone.max_drones

    def connection_has_capacity(
        self,
        zone_a_name: str,
        zone_b_name: str,
        planned_connection_uses: Dict[str, int],
    ) -> bool:
        """Check if a connection can accept one more drone this turn.

        Args:
            zone_a_name: One end of the connection.
            zone_b_name: Other end of the connection.
            planned_connection_uses: Dict of connection key to
                number of drones planned to use it this turn.

        Returns:
            True if the connection can accept one more drone.
        """
        conn = self.graph.get_connection(zone_a_name, zone_b_name)
        if conn is None:
            return False

        key = self._connection_key(zone_a_name, zone_b_name)
        current = self.get_connection_usage(zone_a_name, zone_b_name)
        planned = planned_connection_uses.get(key, 0)

        return (current + planned) < conn.max_link_capacity

    def _connection_key(
        self, zone_a_name: str, zone_b_name: str
    ) -> str:
        """Build a consistent key for a connection regardless of order.

        Always puts the alphabetically first name first so
        hub-roof1 and roof1-hub produce the same key.

        Args:
            zone_a_name: One zone name.
            zone_b_name: Other zone name.

        Returns:
            A consistent string key for this connection.
        """
        names = sorted([zone_a_name, zone_b_name])
        return f"{names[0]}-{names[1]}"
