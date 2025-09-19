"""
Utility functions for the Expense Splitting Calculator application.

This module provides common validation, formatting, and input parsing
functions used throughout the application.
"""

import re
from constants import (
    MAX_NAME_LENGTH,
    NAME_PATTERN,
    MAX_AMOUNT,
    DEFAULT_CURRENCY_SYMBOL,
    ROUNDING_PRECISION,
)


def format_currency(
    amount: float, currency_symbol: str = DEFAULT_CURRENCY_SYMBOL
) -> str:
    """
    Format a monetary amount with proper currency display.

    Args:
        amount: The monetary amount to format
        currency_symbol: Currency symbol to use (default: £)

    Returns:
        Formatted currency string (e.g., "£10.50")
    """
    return f"{currency_symbol}{amount:.{ROUNDING_PRECISION}f}"


def clean_input(text: str) -> str:
    """
    Clean and normalize user input for processing.

    Args:
        text: Raw user input string

    Returns:
        Cleaned input (trimmed and lowercased)
    """
    if not isinstance(text, str):
        return ""
    return text.strip().lower()


def validate_name(name: str, max_length: int = MAX_NAME_LENGTH) -> tuple[bool, str]:
    """
    Validate a person's name according to application rules.

    Args:
        name: Name to validate
        max_length: Maximum allowed length (default from constants)

    Returns:
        Tuple of (is_valid: bool, error_message: str)
    """
    if not isinstance(name, str):
        return False, "Name must be a string"

    cleaned_name = name.strip()

    if not cleaned_name:
        return False, "Name cannot be empty"

    if len(cleaned_name) > max_length:
        return False, f"Name too long (max {max_length} characters)"

    if not re.match(NAME_PATTERN, cleaned_name):
        return (
            False,
            "Name contains invalid characters (use letters, numbers, spaces, hyphens, underscores, dots)",
        )

    return True, ""


def parse_amount_input(input_str: str) -> tuple[bool, float, str]:
    """
    Parse and validate monetary amount input from user.

    Args:
        input_str: User input string (may contain currency symbols)

    Returns:
        Tuple of (is_valid: bool, amount: float, error_message: str)
    """
    if not isinstance(input_str, str):
        return False, 0.0, "Input must be a string"

    # Remove common currency symbols
    cleaned = input_str.strip().replace("£", "").replace("$", "").replace("€", "")

    try:
        amount = float(cleaned)

        if amount <= 0:
            return False, 0.0, "Amount must be positive"

        if amount > MAX_AMOUNT:
            return False, 0.0, f"Amount too large (max {format_currency(MAX_AMOUNT)})"

        # Validate decimal places
        if "." in cleaned and len(cleaned.split(".")[1]) > ROUNDING_PRECISION:
            return (
                False,
                0.0,
                f"Amount cannot have more than {ROUNDING_PRECISION} decimal places",
            )

        return True, round(amount, ROUNDING_PRECISION), ""

    except ValueError:
        return False, 0.0, "Invalid amount format"


def is_valid_money(value) -> bool:
    """
    Check if a value represents a valid monetary amount.

    Validates that the value is numeric, finite, and has at most
    two decimal places for currency precision.

    Args:
        value: Value to validate (any type)

    Returns:
        True if valid monetary amount, False otherwise
    """
    if not isinstance(value, (int, float)):
        return False

    # Check for infinite values
    if not (float("-inf") < value < float("inf")):
        return False

    # Check for NaN
    if value != value:  # NaN is not equal to itself
        return False

    # Validate decimal places precision
    value_str = f"{value:.10f}".rstrip("0").rstrip(".")
    if "." in value_str:
        decimals = value_str.split(".")[1]
        return len(decimals) <= ROUNDING_PRECISION

    return True
