"""Drone path scheduler using Dijkstra for route planning."""

from typing import List, Dict, Optional
from models.drone import Drone
from models.graph import Graph
from models.zone import Zone
from simulation.state import SimulationState
from pathfinding.dijkstra import Dijkstra


class Scheduler:
    """Assigns paths to drones and decides next moves.

    Uses Dijkstra to find all paths, distributes drones
    across them, and handles waiting when zones are full.

    Attributes:
        graph: The routing graph.
        dijkstra: The pathfinding algorithm instance.
        drone_paths: Path assigned to each drone by id.
        drone_progress: How far along its path each drone is.
        all_paths: All discovered paths sorted by cost.
        paths_found: Whether path discovery has run yet.
    """

    def __init__(self, graph: Graph) -> None:
        """Initialize the scheduler with a graph.

        Args:
            graph: The routing graph.
        """
        self.graph: Graph = graph
        self.dijkstra: Dijkstra = Dijkstra(graph)
        self.drone_paths: Dict[int, List[str]] = {}
        self.drone_progress: Dict[int, int] = {}
        self.all_paths: List[List[str]] = []
        self.paths_found: bool = False

    def _find_all_paths(self) -> None:
        """Find all simple paths from start to end zone.

        Uses repeated Dijkstra calls with zone exclusions to
        discover multiple distinct paths. Sorts by path cost.
        """
        if (
            self.graph.start_zone is None
            or self.graph.end_zone is None
        ):
            return

        start = self.graph.start_zone.name
        end = self.graph.end_zone.name

        found: List[List[str]] = []
        excluded: set = set()

        for _ in range(10):
            path = self.dijkstra.find_path_excluding(
                start, end, excluded
            )
            if path is None:
                break
            if path in found:
                break
            found.append(path)
            middle_zones = path[1:-1]
            if middle_zones:
                excluded.add(middle_zones[0])

        if not found:
            path = self.dijkstra.find_path(start, end)
            if path is not None:
                found.append(path)

        self.all_paths = sorted(found, key=self._path_cost)

    def _path_cost(self, path: List[str]) -> float:
        """Calculate the total movement cost of a path.

        Used to sort paths from cheapest to most expensive.

        Args:
            path: List of zone names representing a path.

        Returns:
            Total float cost of travelling the full path.
        """
        total: float = 0.0
        for zone_name in path[1:]:
            zone = self.graph.get_zone(zone_name)
            if zone is None:
                continue
            if zone.zone_type.value == "priority":
                total += 0.9
            else:
                total += float(zone.movement_cost())
        return total

    def _assign_paths(self, drones: List[Drone]) -> None:
        """Assign each drone a path using round-robin distribution.

        Spreads drones evenly across all available paths so
        they move in parallel rather than queuing on one path.

        Args:
            drones: All drones to assign paths to.
        """
        if not self.all_paths:
            return

        for i, drone in enumerate(drones):
            path_index = i % len(self.all_paths)
            assigned_path = self.all_paths[path_index]
            self.drone_paths[drone.drone_id] = assigned_path
            self.drone_progress[drone.drone_id] = 0

    def get_next_zone(
        self,
        drone: Drone,
        graph: Graph,
        state: SimulationState,
    ) -> Optional[Zone]:
        """Return the next zone for a drone to move to.

        Called by the engine every turn for every active drone.
        Returns None if the drone should wait this turn.

        Args:
            drone: The drone to plan for.
            graph: The routing graph.
            state: Current simulation state.

        Returns:
            The next Zone to move to, or None to wait.
        """
        if not self.paths_found:
            self._find_all_paths()
            self._assign_paths(state.get_active_drones())
            self.paths_found = True

        drone_id = drone.drone_id

        if drone_id not in self.drone_paths:
            return None

        path = self.drone_paths[drone_id]
        progress = self.drone_progress[drone_id]

        if progress + 1 >= len(path):
            return None

        next_zone_name = path[progress + 1]
        next_zone = self.graph.get_zone(next_zone_name)

        if next_zone is None:
            return None

        return next_zone

    def confirm_move(self, drone: Drone) -> None:
        """Confirm a drone's move was accepted by the engine.

        Only called after the engine validates and applies the move.

        Args:
            drone: The drone that successfully moved.
        """
        if drone.drone_id in self.drone_progress:
            self.drone_progress[drone.drone_id] += 1
