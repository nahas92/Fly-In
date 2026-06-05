"""Entry point for the Fly-in drone routing simulation."""

from parser.map_parser import MapParser
from simulation.engine import SimulationEngine
from pathfinding.scheduler import Scheduler
from visualization.terminal import TerminalVisualizer


def main() -> None:
    """Run the simulation."""
    parser = MapParser()
    graph = parser.parse("maps/test_simple.txt")

    scheduler = Scheduler(graph)
    engine = SimulationEngine(graph, scheduler)
    visualizer = TerminalVisualizer(graph)

    turns = engine.run(visualizer)
    visualizer.print_summary(turns, graph.nb_drones)


if __name__ == "__main__":
    main()
