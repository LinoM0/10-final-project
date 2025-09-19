# Constants and utilities for the expense splitting application

import re


def format_currency(amount: float, currency_symbol: str = "£") -> str:
    """
    Format a monetary amount with proper currency display.

    :param amount: The monetary amount
    :param currency_symbol: Currency symbol to use
    :return: Formatted currency string
    """
    return f"{currency_symbol}{amount:.2f}"


def clean_input(text: str) -> str:
    """
    Clean and normalize user input.

    :param text: Raw user input
    :return: Cleaned input
    """
    if not isinstance(text, str):
        return ""

    # Remove extra whitespace and convert to lowercase for processing
    return text.strip().lower()


def validate_name(name: str, max_length: int = 50) -> tuple[bool, str]:
    """
    Validate a person's name.

    :param name: Name to validate
    :param max_length: Maximum allowed length
    :return: (is_valid, error_message)
    """
    if not isinstance(name, str):
        return False, "Name must be a string"

    cleaned_name = name.strip()

    if not cleaned_name:
        return False, "Name cannot be empty"

    if len(cleaned_name) > max_length:
        return False, f"Name too long (max {max_length} characters)"

    if not re.match(r"^[a-zA-Z0-9\s\-_\.]+$", cleaned_name):
        return (
            False,
            "Name contains invalid characters (use letters, numbers, spaces, hyphens, underscores, dots)",
        )

    return True, ""


def parse_amount_input(input_str: str) -> tuple[bool, float, str]:
    """
    Parse and validate monetary amount input.

    :param input_str: User input string
    :return: (is_valid, amount, error_message)
    """
    if not isinstance(input_str, str):
        return False, 0.0, "Input must be a string"

    # Clean input - remove currency symbols
    cleaned = input_str.strip().replace("£", "").replace("$", "").replace("€", "")

    try:
        amount = float(cleaned)

        if amount <= 0:
            return False, 0.0, "Amount must be positive"

        if amount > 999999.99:
            return False, 0.0, "Amount too large (max £999,999.99)"

        # Check decimal places
        if "." in cleaned and len(cleaned.split(".")[1]) > 2:
            return False, 0.0, "Amount cannot have more than 2 decimal places"

        return True, round(amount, 2), ""

    except ValueError:
        return False, 0.0, "Invalid amount format"


def is_valid_money(value) -> bool:
    """
    Check if a value is a valid monetary amount (at most two decimal places).
    :param value: Value to check (any type)
    :return: True if valid, False otherwise
    """
    if not isinstance(value, (int, float)):
        return False

    # Check for special float values
    if not (float("-inf") < value < float("inf")):
        return False

    # Ensure it's not NaN
    if value != value:  # NaN check
        return False

    # Check decimal places precision
    value_str = f"{value:.10f}".rstrip("0").rstrip(".")
    if "." in value_str:
        decimals = value_str.split(".")[1]
        return len(decimals) <= 2
    return True
