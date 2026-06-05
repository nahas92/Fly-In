"""Simulation engine that routes drones turn by turn."""

from typing import List, Dict, Any, Optional
from models.drone import Drone
from models.zone import Zone, ZoneType
from models.graph import Graph
from simulation.state import SimulationState


class PlannedMove:
    """Represents one drone's intended action for a turn.

    Attributes:
        drone: The drone being moved.
        destination: The zone the drone is moving to.
        is_restricted: Whether this is a 2-turn restricted move.
        connection_key: Key of the connection being used.
    """

    def __init__(
        self,
        drone: Drone,
        destination: Zone,
        is_restricted: bool,
        connection_key: str,
    ) -> None:
        """Initialize a PlannedMove.

        Args:
            drone: The drone being moved.
            destination: The target zone.
            is_restricted: True if destination is restricted.
            connection_key: Consistent key for the connection.
        """
        self.drone: Drone = drone
        self.destination: Zone = destination
        self.is_restricted: bool = is_restricted
        self.connection_key: str = connection_key


class SimulationEngine:
    """Runs the drone routing simulation turn by turn.

    Uses a pathfinding algorithm to decide moves and enforces
    all movement and capacity rules from the subject.

    Attributes:
        graph: The routing graph.
        state: Current simulation state.
        algorithm: The pathfinding algorithm to use.
    """

    def __init__(
        self,
        graph: Graph,
        algorithm: Any,
    ) -> None:
        """Initialize the engine with a graph and algorithm.

        Args:
            graph: The routing graph.
            algorithm: Pathfinding algorithm with get_next_zone().
        """
        self.graph: Graph = graph
        self.algorithm: Any = algorithm

        if graph.start_zone is None:
            raise ValueError(
                "Graph has no start zone defined."
            )

        drones: List[Drone] = [
            Drone(i + 1, graph.start_zone)
            for i in range(graph.nb_drones)
        ]
        self.state: SimulationState = SimulationState(
            graph, drones
        )

    def run(self, visualizer: Optional[Any] = None) -> int:
        """Run the simulation until all drones are delivered.

        Args:
            visualizer: Optional terminal visualizer.

        Returns:
            Total number of turns taken.
        """
        while not self.state.all_delivered():
            self.state.turn += 1
            output = self._run_turn()
            if output:
                if visualizer is not None:
                    visualizer.print_turn(self.state.turn, output)
                else:
                    print(output)
        return self.state.turn

    def _run_turn(self) -> str:
        """Execute one complete simulation turn.

        Returns:
            The output line for this turn.
        """
        planned_exits: Dict[str, int] = {}
        planned_entries: Dict[str, int] = {}
        planned_connection_uses: Dict[str, int] = {}
        planned_moves: List[PlannedMove] = []

        self._plan_moves(
            planned_moves,
            planned_exits,
            planned_entries,
            planned_connection_uses,
        )

        self._apply_moves(planned_moves)

        return self._build_output(planned_moves)

    def _plan_moves(
        self,
        planned_moves: List[PlannedMove],
        planned_exits: Dict[str, int],
        planned_entries: Dict[str, int],
        planned_connection_uses: Dict[str, int],
    ) -> None:
        """Decide what each active drone will do this turn.

        Args:
            planned_moves: List to append valid moves into.
            planned_exits: Tracks drones leaving each zone.
            planned_connection_uses: Tracks connection usage.
        """
        for drone in self.state.get_active_drones():
            if drone.is_in_transit():
                self._plan_transit_arrival(
                    drone,
                    planned_moves,
                    planned_exits,
                    planned_entries,
                    planned_connection_uses,
                )
            else:
                self._plan_new_move(
                    drone,
                    planned_moves,
                    planned_exits,
                    planned_entries,
                    planned_connection_uses,
                )

    def _plan_transit_arrival(
        self,
        drone: Drone,
        planned_moves: List[PlannedMove],
        planned_exits: Dict[str, int],
        planned_entries: Dict[str, int],
        planned_connection_uses: Dict[str, int],
    ) -> None:
        """Plan the arrival of a drone mid-flight to restricted zone.

        A drone in transit MUST arrive this turn — no waiting.

        Args:
            drone: The drone in transit.
            planned_moves: List to append the move into.
            planned_exits: Tracks drones leaving each zone.
            planned_connection_uses: Tracks connection usage.
        """
        if drone.in_transit_to is None:
            return

        destination = drone.in_transit_to
        conn_key = self.state._connection_key(
            drone.current_zone.name,
            destination.name,
        )

        move = PlannedMove(
            drone=drone,
            destination=destination,
            is_restricted=True,
            connection_key=conn_key,
        )
        planned_moves.append(move)

        planned_exits[drone.current_zone.name] = (
            planned_exits.get(drone.current_zone.name, 0) + 1
        )
        planned_entries[destination.name] = (
            planned_entries.get(destination.name, 0) + 1
        )

    def _plan_new_move(
        self,
        drone: Drone,
        planned_moves: List[PlannedMove],
        planned_exits: Dict[str, int],
        planned_entries: Dict[str, int],
        planned_connection_uses: Dict[str, int],
    ) -> None:
        """Plan a new move for a drone currently sitting in a zone.

        Asks the algorithm for the next zone. Checks all capacity
        rules before committing the move.

        Args:
            drone: The drone to plan for.
            planned_moves: List to append valid moves into.
            planned_exits: Tracks drones leaving each zone.
            planned_connection_uses: Tracks connection usage.
        """
        next_zone = self.algorithm.get_next_zone(
            drone, self.graph, self.state
        )

        if next_zone is None:
            return

        if next_zone.zone_type == ZoneType.BLOCKED:
            return

        conn_key = self.state._connection_key(
            drone.current_zone.name,
            next_zone.name,
        )

        zone_ok = self.state.zone_has_capacity(
            next_zone.name, planned_exits, planned_entries
        )
        conn_ok = self.state.connection_has_capacity(
            drone.current_zone.name,
            next_zone.name,
            planned_connection_uses,
        )

        if not zone_ok or not conn_ok:
            return

        is_restricted = (
            next_zone.zone_type == ZoneType.RESTRICTED
        )

        move = PlannedMove(
            drone=drone,
            destination=next_zone,
            is_restricted=is_restricted,
            connection_key=conn_key,
        )
        planned_moves.append(move)

        planned_exits[drone.current_zone.name] = (
            planned_exits.get(drone.current_zone.name, 0) + 1
        )
        planned_entries[next_zone.name] = (
            planned_entries.get(next_zone.name, 0) + 1
        )
        planned_connection_uses[conn_key] = (
            planned_connection_uses.get(conn_key, 0) + 1
        )

    def _apply_moves(
        self, planned_moves: List[PlannedMove]
    ) -> None:
        """Apply all planned moves simultaneously.

        Args:
            planned_moves: All moves decided for this turn.
        """
        end_zone = self.graph.end_zone

        for move in planned_moves:
            drone = move.drone
            destination = move.destination

            if move.is_restricted and drone.in_transit_to is None:
                drone.in_transit_to = destination
                drone.turns_in_transit = 1
            else:
                drone.current_zone = destination
                drone.in_transit_to = None
                drone.turns_in_transit = 0

                if (
                    end_zone is not None
                    and destination.name == end_zone.name
                ):
                    drone.delivered = True

                if hasattr(self.algorithm, "confirm_move"):
                    self.algorithm.confirm_move(drone)

    def _build_output(
        self, planned_moves: List[PlannedMove]
    ) -> str:
        """Build the output line for this turn.

        Format: D<id>-<zone> for normal moves.
        Format: D<id>-<zone_a>_<zone_b> for restricted transit.
        Stationary drones are omitted.

        Args:
            planned_moves: All moves that happened this turn.

        Returns:
            Space-separated string of drone movements.
        """
        parts: List[str] = []

        for move in planned_moves:
            drone = move.drone
            if move.is_restricted and drone.in_transit_to is not None:
                label = (
                    f"{drone.label()}-"
                    f"{drone.current_zone.name}_"
                    f"{move.destination.name}"
                )
            else:
                label = (
                    f"{drone.label()}-{move.destination.name}"
                )
            parts.append(label)

        return " ".join(parts)
