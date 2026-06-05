"""Dijkstra pathfinding for the drone routing graph."""

import heapq
from typing import List, Dict, Optional
from models.graph import Graph


class Dijkstra:
    """Finds shortest weighted paths through the graph.

    Uses Dijkstra's algorithm with zone movement costs as weights.
    Blocked zones are never added to paths.
    Priority zones get a slight cost advantage.

    Attributes:
        graph: The routing graph to search through.
    """

    def __init__(self, graph: Graph) -> None:
        """Initialize Dijkstra with a graph.

        Args:
            graph: The routing graph.
        """
        self.graph: Graph = graph

    def find_path(
        self,
        start_name: str,
        end_name: str,
    ) -> Optional[List[str]]:
        """Find the shortest weighted path between two zones.

        Args:
            start_name: Name of the starting zone.
            end_name: Name of the destination zone.

        Returns:
            Ordered list of alternativezone names from start to end,
            or None if no path exists.
        """
        if start_name == end_name:
            return [start_name]

        known_cost: Dict[str, float] = {}
        came_from: Dict[str, Optional[str]] = {}
        priority_queue: List = []

        known_cost[start_name] = 0.0
        came_from[start_name] = None
        heapq.heappush(priority_queue, (0.0, start_name))

        while priority_queue:
            cost, current_name = heapq.heappop(priority_queue)

            if current_name == end_name:
                break

            if cost > known_cost.get(current_name, float("inf")):
                continue

            for neighbor in self.graph.get_neighbors(current_name):
                if neighbor.zone_type.value == "blocked":
                    continue

                if neighbor.zone_type.value == "priority":
                    move_cost = 0.9
                else:
                    move_cost = float(neighbor.movement_cost())

                new_cost = cost + move_cost

                if new_cost < known_cost.get(
                    neighbor.name, float("inf")
                ):
                    known_cost[neighbor.name] = new_cost
                    came_from[neighbor.name] = current_name
                    heapq.heappush(
                        priority_queue,
                        (new_cost, neighbor.name)
                    )

        if end_name not in came_from:
            return None

        path: List[str] = []
        current: Optional[str] = end_name

        while current is not None:
            path.append(current)
            current = came_from.get(current)

        path.reverse()
        return path

    def find_path_excluding(
        self,
        start_name: str,
        end_name: str,
        excluded: set,
    ) -> Optional[List[str]]:
        """Find shortest path while excluding specific zones.

        Identical to find_path but skips any zone in excluded.
        Used to discover alternative paths.

        Args:
            start_name: Name of the starting zone.
            end_name: Name of the destination zone.
            excluded: Set of zone names to skip entirely.

        Returns:
            Ordered list of zone names, or None if no path exists.
        """
        if start_name == end_name:
            return [start_name]

        known_cost: Dict[str, float] = {}
        came_from: Dict[str, Optional[str]] = {}
        priority_queue: List = []

        known_cost[start_name] = 0.0
        came_from[start_name] = None
        heapq.heappush(priority_queue, (0.0, start_name))

        while priority_queue:
            cost, current_name = heapq.heappop(priority_queue)

            if current_name == end_name:
                break

            if cost > known_cost.get(current_name, float("inf")):
                continue

            for neighbor in self.graph.get_neighbors(current_name):
                if neighbor.zone_type.value == "blocked":
                    continue

                if neighbor.name in excluded:
                    continue

                if neighbor.zone_type.value == "priority":
                    move_cost = 0.9
                else:
                    move_cost = float(neighbor.movement_cost())

                new_cost = cost + move_cost

                if new_cost < known_cost.get(
                    neighbor.name, float("inf")
                ):
                    known_cost[neighbor.name] = new_cost
                    came_from[neighbor.name] = current_name
                    heapq.heappush(
                        priority_queue,
                        (new_cost, neighbor.name)
                    )

        if end_name not in came_from:
            return None

        path: List[str] = []
        current: Optional[str] = end_name

        while current is not None:
            path.append(current)
            current = came_from.get(current)

        path.reverse()
        return path
