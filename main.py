"""Entry point for the Fly-in drone routing simulation."""

import sys
from parser.map_parser import MapParser
from simulation.engine import SimulationEngine
from pathfinding.scheduler import Scheduler
from visualization.terminal import TerminalVisualizer


def main() -> None:
    """Run the simulation."""
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <map_file>")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        parser = MapParser()
        graph = parser.parse(filepath)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    scheduler = Scheduler(graph)
    engine = SimulationEngine(graph, scheduler)
    visualizer = TerminalVisualizer(graph)

    turns = engine.run(visualizer)
    visualizer.print_summary(turns, graph.nb_drones)


if __name__ == "__main__":
    main()
