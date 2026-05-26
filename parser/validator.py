"""Validation logic for map file parsing."""


class Validator:
    """Validates map file lines and values during parsing.

    Each method checks one specific rule from the subject.
    Raises ValueError with a clear message on any violation.
    """

    VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}

    def validate_nb_drones(
        self, value: str, line_number: int
    ) -> int:
        """Validate and parse the nb_drones value.

        Args:
            value: The raw string value after 'nb_drones:'.
            line_number: Line number for error reporting.

        Returns:
            The number of drones as a positive integer.

        Raises:
            ValueError: If value is not a positive integer.
        """
        try:
            nb = int(value.strip())
        except ValueError:
            raise ValueError(
                f"Line {line_number}: nb_drones must be an"
                f" integer, got '{value.strip()}'"
            )
        if nb <= 0:
            raise ValueError(
                f"Line {line_number}: nb_drones must be"
                f" positive, got {nb}"
            )
        return nb

    def validate_zone_name(
        self, name: str, line_number: int
    ) -> None:
        """Validate a zone name contains no dashes or spaces.

        Args:
            name: The zone name to check.
            line_number: Line number for error reporting.

        Raises:
            ValueError: If name contains a dash or space.
        """
        if "-" in name:
            raise ValueError(
                f"Line {line_number}: zone name '{name}'"
                f" must not contain dashes"
            )
        if " " in name:
            raise ValueError(
                f"Line {line_number}: zone name '{name}'"
                f" must not contain spaces"
            )

    def validate_coordinates(
        self, x_str: str, y_str: str, line_number: int
    ) -> tuple[int, int]:
        """Validate and parse zone coordinates.

        Args:
            x_str: Raw string for x coordinate.
            y_str: Raw string for y coordinate.
            line_number: Line number for error reporting.

        Returns:
            Tuple of (x, y) as integers.

        Raises:
            ValueError: If coordinates are not integers.
        """
        try:
            x = int(x_str.strip())
            y = int(y_str.strip())
        except ValueError:
            raise ValueError(
                f"Line {line_number}: coordinates must be"
                f" integers, got '{x_str}' '{y_str}'"
            )
        return x, y

    def validate_zone_type(
        self, zone_type: str, line_number: int
    ) -> None:
        """Validate a zone type string is one of the four valid types.

        Args:
            zone_type: The zone type string to check.
            line_number: Line number for error reporting.

        Raises:
            ValueError: If zone_type is not a valid type.
        """
        if zone_type not in self.VALID_ZONE_TYPES:
            raise ValueError(
                f"Line {line_number}: invalid zone type"
                f" '{zone_type}'. Must be one of:"
                f" {self.VALID_ZONE_TYPES}"
            )

    def validate_capacity(
        self, value: str, field_name: str, line_number: int
    ) -> int:
        """Validate a capacity value is a positive integer.

        Used for both max_drones and max_link_capacity.

        Args:
            value: Raw string capacity value.
            field_name: Name of the field for error messages.
            line_number: Line number for error reporting.

        Returns:
            The capacity as a positive integer.

        Raises:
            ValueError: If value is not a positive integer.
        """
        try:
            capacity = int(value.strip())
        except ValueError:
            raise ValueError(
                f"Line {line_number}: {field_name} must be"
                f" an integer, got '{value.strip()}'"
            )
        if capacity <= 0:
            raise ValueError(
                f"Line {line_number}: {field_name} must be"
                f" positive, got {capacity}"
            )
        return capacity

    def validate_connection_zones(
        self,
        zone_a_name: str,
        zone_b_name: str,
        defined_zones: set,
        line_number: int,
    ) -> None:
        """Validate both zones in a connection are already defined.

        Args:
            zone_a_name: Name of the first zone.
            zone_b_name: Name of the second zone.
            defined_zones: Set of all zone names defined so far.
            line_number: Line number for error reporting.

        Raises:
            ValueError: If either zone was not previously defined.
        """
        if zone_a_name not in defined_zones:
            raise ValueError(
                f"Line {line_number}: connection references"
                f" undefined zone '{zone_a_name}'"
            )
        if zone_b_name not in defined_zones:
            raise ValueError(
                f"Line {line_number}: connection references"
                f" undefined zone '{zone_b_name}'"
            )
