"""Colored terminal visualization for the simulation."""

from models.graph import Graph


RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
WHITE = "\033[97m"


class TerminalVisualizer:
    """Prints colored terminal output for each simulation turn.

    Attributes:
        graph: The routing graph for zone type lookups.
    """

    def __init__(self, graph: Graph) -> None:
        """Initialize the visualizer.

        Args:
            graph: The routing graph.
        """
        self.graph: Graph = graph

    def print_turn(self, turn: int, output: str) -> None:
        """Print one simulation turn with colors.

        Args:
            turn: The current turn number.
            output: The raw output string for this turn.
        """
        if not output:
            return

        print(f"{BOLD}{YELLOW}Turn {turn}:{RESET}")

        parts = output.split(" ")
        colored_parts = []

        for part in parts:
            colored_parts.append(self._color_part(part))

        print("  " + " ".join(colored_parts))
        print()

    def _color_part(self, part: str) -> str:
        """Color one drone movement token.

        Args:
            part: A single movement like D1-zoneA or D2-hub_roof1.

        Returns:
            The part with ANSI color codes applied.
        """
        if "-" not in part:
            return part

        dash = part.index("-")
        drone_label = part[:dash]
        destination = part[dash + 1:]

        colored_drone = f"{CYAN}{drone_label}{RESET}"

        if "_" in destination:
            colored_dest = f"{RED}{destination}{RESET}"
        else:
            zone = self.graph.get_zone(destination)
            if zone is None:
                colored_dest = f"{WHITE}{destination}{RESET}"
            elif zone.zone_type.value == "restricted":
                colored_dest = f"{RED}{destination}{RESET}"
            elif zone.zone_type.value == "priority":
                colored_dest = f"{GREEN}{destination}{RESET}"
            else:
                colored_dest = f"{WHITE}{destination}{RESET}"

        return f"{colored_drone}-{colored_dest}"

    def print_summary(self, turns: int, nb_drones: int) -> None:
        """Print the final simulation summary.

        Args:
            turns: Total turns taken.
            nb_drones: Total number of drones routed.
        """
        print(f"{BOLD}{GREEN}Simulation complete!{RESET}")
        print(
            f"  Drones delivered: {CYAN}{nb_drones}{RESET}"
        )
        print(
            f"  Total turns:      {CYAN}{turns}{RESET}"
        )
