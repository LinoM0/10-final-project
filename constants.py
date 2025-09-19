"""
Constants for the Expense Splitting Calculator application.

This module contains all configuration values, limits, and constants
used throughout the application for better maintainability.
"""

# Person and Name Validation
MAX_NAME_LENGTH = 50
NAME_PATTERN = r"^[a-zA-Z0-9\s\-_\.]+$"

# Monetary Constraints
MIN_AMOUNT = 0.01
MAX_AMOUNT = 999999.99

# System Limits
MAX_PARTICIPANTS = 100
MAX_PEOPLE = 1000

# Split Strategy Validation
MIN_WEIGHT = 0.01
MAX_WEIGHT = 1000000
MIN_PERCENTAGE = 0.01
MAX_PERCENTAGE = 100.0
PERCENTAGE_TOLERANCE = 0.01

# Settlement Configuration
SETTLEMENT_TOLERANCE = 0.01  # 1 cent tolerance for settlement
ROUNDING_PRECISION = 2  # Round to 2 decimal places for currency

# UI Configuration
DEFAULT_CURRENCY_SYMBOL = "£"

# Menu Options
MENU_OPTIONS = {
    "1": "add_person",
    "2": "add_expense",
    "3": "view_people",
    "4": "view_expenses",
    "5": "view_balances",
    "6": "show_summary",
    "7": "settle_debts",
    "8": "exit",
}

SPLIT_TYPES = {"1": "equal", "2": "weights", "3": "percent", "4": "exact"}
