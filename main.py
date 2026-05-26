"""Entry point for the Fly-in drone routing simulation."""

from parser.map_parser import MapParser
from simulation.engine import SimulationEngine
from models.graph import Graph
from simulation.state import SimulationState
from models.drone import Drone
from models.zone import Zone
from typing import Optional


class SimpleAlgorithm:
    """Temporary stub algorithm that moves drones forward."""

    def get_next_zone(
        self,
        drone: Drone,
        graph: Graph,
        state: SimulationState,
    ) -> Optional[Zone]:
        """Return first valid neighbor of drone's current zone."""
        neighbors = graph.get_neighbors(
            drone.current_zone.name
        )
        for zone in neighbors:
            return zone
        return None


def main() -> None:
    """Run the simulation."""
    parser = MapParser()
    graph = parser.parse("maps/test_simple.txt")

    algorithm = SimpleAlgorithm()
    engine = SimulationEngine(graph, algorithm)
    turns = engine.run()
    print(f"Completed in {turns} turns")


if __name__ == "__main__":
    main()
