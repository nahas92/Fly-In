"""Map file parser that builds a Graph from a .txt map file."""

from typing import Optional
from models.zone import Zone, ZoneType
from models.connection import Connection
from models.graph import Graph
from parser.validator import Validator


class MapParser:
    """Reads a map file and constructs a Graph object.

    Processes the file line by line, validates each line,
    and builds the graph incrementally.

    Attributes:
        validator: The validator used to check all values.
        graph: The graph being built during parsing.
        defined_zones: Zone names seen so far for connection checks.
        start_hub_count: Tracks how many start hubs were defined.
        end_hub_count: Tracks how many end hubs were defined.
    """

    def __init__(self) -> None:
        """Initialize the parser with a fresh graph and validator."""
        self.validator: Validator = Validator()
        self.graph: Graph = Graph()
        self.defined_zones: set = set()
        self.start_hub_count: int = 0
        self.end_hub_count: int = 0

    def parse(self, filepath: str) -> Graph:
        """Parse a map file and return the built Graph.

        Args:
            filepath: Path to the map file to parse.

        Returns:
            A fully constructed Graph object.

        Raises:
            ValueError: If any line contains a parsing error.
            FileNotFoundError: If the file does not exist.
        """
        try:
            with open(filepath, "r") as f:
                lines = f.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Map file not found: '{filepath}'"
            )

        for line_number, raw_line in enumerate(lines, start=1):
            self._parse_line(raw_line, line_number)

        self._validate_final_state()
        return self.graph

    def _parse_line(self, raw_line: str, line_number: int) -> None:
        """Parse a single line from the map file.

        Args:
            raw_line: The raw string from the file.
            line_number: The line number for error reporting.
        """
        line = raw_line.strip()

        if not line or line.startswith("#"):
            return

        if ":" not in line:
            raise ValueError(
                f"Line {line_number}: unrecognised format"
                f" '{line}'"
            )

        keyword, rest = line.split(":", 1)
        keyword = keyword.strip()
        rest = rest.strip()

        if keyword == "nb_drones":
            self._parse_nb_drones(rest, line_number)
        elif keyword == "start_hub":
            self._parse_zone(rest, line_number, is_start=True)
        elif keyword == "end_hub":
            self._parse_zone(rest, line_number, is_end=True)
        elif keyword == "hub":
            self._parse_zone(rest, line_number)
        elif keyword == "connection":
            self._parse_connection(rest, line_number)
        else:
            raise ValueError(
                f"Line {line_number}: unknown keyword"
                f" '{keyword}'"
            )

    def _parse_nb_drones(
        self, rest: str, line_number: int
    ) -> None:
        """Parse the nb_drones line.

        Args:
            rest: Everything after 'nb_drones:'.
            line_number: Line number for error reporting.
        """
        if line_number != 1:
            raise ValueError(
                f"Line {line_number}: nb_drones must be"
                f" the first line"
            )
        self.graph.nb_drones = self.validator.validate_nb_drones(
            rest, line_number
        )

    def _parse_zone(
        self,
        rest: str,
        line_number: int,
        is_start: bool = False,
        is_end: bool = False,
    ) -> None:
        """Parse a hub, start_hub, or end_hub line.

        Args:
            rest: Everything after the keyword and colon.
            line_number: Line number for error reporting.
            is_start: True if this is the start hub.
            is_end: True if this is the end hub.
        """
        metadata, rest_without_meta = self._extract_metadata(
            rest, line_number
        )

        parts = rest_without_meta.split()

        if len(parts) < 3:
            raise ValueError(
                f"Line {line_number}: zone definition needs"
                f" name x y, got '{rest_without_meta}'"
            )

        name = parts[0]
        self.validator.validate_zone_name(name, line_number)

        x, y = self.validator.validate_coordinates(
            parts[1], parts[2], line_number
        )

        zone_type = ZoneType.NORMAL
        color: Optional[str] = None
        max_drones = 1

        for key, value in metadata.items():
            if key == "zone":
                self.validator.validate_zone_type(
                    value, line_number
                )
                zone_type = ZoneType(value)
            elif key == "color":
                color = value
            elif key == "max_drones":
                max_drones = self.validator.validate_capacity(
                    value, "max_drones", line_number
                )
            else:
                raise ValueError(
                    f"Line {line_number}: unknown metadata"
                    f" key '{key}'"
                )

        zone = Zone(
            name=name,
            x=x,
            y=y,
            zone_type=zone_type,
            color=color,
            max_drones=max_drones,
        )

        try:
            self.graph.add_zone(zone)
        except ValueError as e:
            raise ValueError(f"Line {line_number}: {e}")

        self.defined_zones.add(name)

        if is_start:
            self.start_hub_count += 1
            self.graph.start_zone = zone
        if is_end:
            self.end_hub_count += 1
            self.graph.end_zone = zone

    def _parse_connection(
        self, rest: str, line_number: int
    ) -> None:
        """Parse a connection line.

        Args:
            rest: Everything after 'connection:'.
            line_number: Line number for error reporting.
        """
        metadata, rest_without_meta = self._extract_metadata(
            rest, line_number
        )

        parts = rest_without_meta.strip().split("-")

        if len(parts) != 2:
            raise ValueError(
                f"Line {line_number}: connection must be"
                f" 'zone1-zone2', got '{rest_without_meta}'"
            )

        zone_a_name = parts[0].strip()
        zone_b_name = parts[1].strip()

        self.validator.validate_connection_zones(
            zone_a_name, zone_b_name,
            self.defined_zones, line_number
        )

        max_link_capacity = 1
        for key, value in metadata.items():
            if key == "max_link_capacity":
                max_link_capacity = self.validator.validate_capacity(
                    value, "max_link_capacity", line_number
                )
            else:
                raise ValueError(
                    f"Line {line_number}: unknown connection"
                    f" metadata key '{key}'"
                )

        zone_a = self.graph.get_zone(zone_a_name)
        zone_b = self.graph.get_zone(zone_b_name)

        if zone_a is None or zone_b is None:
            raise ValueError(
                f"Line {line_number}: could not retrieve"
                f" zone from graph"
            )

        connection = Connection(
            zone_a=zone_a,
            zone_b=zone_b,
            max_link_capacity=max_link_capacity,
        )

        try:
            self.graph.add_connection(connection)
        except ValueError as e:
            raise ValueError(f"Line {line_number}: {e}")

    def _extract_metadata(
        self, rest: str, line_number: int
    ) -> tuple[dict, str]:
        """Extract and parse the optional metadata block.

        Splits the line into metadata dict and the remaining text.

        Args:
            rest: The part of the line after the keyword colon.
            line_number: Line number for error reporting.

        Returns:
            Tuple of (metadata dict, rest of line without metadata).

        Raises:
            ValueError: If the metadata block is malformed.
        """
        metadata: dict = {}

        if "[" not in rest:
            return metadata, rest

        if "]" not in rest:
            raise ValueError(
                f"Line {line_number}: metadata block opened"
                f" with '[' but never closed"
            )

        bracket_open = rest.index("[")
        bracket_close = rest.index("]")

        if bracket_open > bracket_close:
            raise ValueError(
                f"Line {line_number}: metadata block"
                f" malformed, ']' before '['"
            )

        rest_without_meta = rest[:bracket_open].strip()
        meta_content = rest[bracket_open + 1:bracket_close]

        if not meta_content.strip():
            return metadata, rest_without_meta

        pairs = meta_content.strip().split()

        for pair in pairs:
            if "=" not in pair:
                raise ValueError(
                    f"Line {line_number}: metadata '{pair}'"
                    f" missing '='"
                )
            key, value = pair.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key or not value:
                raise ValueError(
                    f"Line {line_number}: metadata key or"
                    f" value is empty in '{pair}'"
                )
            metadata[key] = value

        return metadata, rest_without_meta

    def _validate_final_state(self) -> None:
        """Check global rules after all lines are parsed.

        Raises:
            ValueError: If start or end hub counts are wrong.
        """
        if self.start_hub_count == 0:
            raise ValueError(
                "No start_hub defined in map file"
            )
        if self.start_hub_count > 1:
            raise ValueError(
                "Multiple start_hub definitions found"
            )
        if self.end_hub_count == 0:
            raise ValueError(
                "No end_hub defined in map file"
            )
        if self.end_hub_count > 1:
            raise ValueError(
                "Multiple end_hub definitions found"
            )
        if self.graph.nb_drones == 0:
            raise ValueError(
                "nb_drones was never defined"
            )
