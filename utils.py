# Constants and utilities for the expense splitting application

import re
from typing import Union, List, Dict, Any


def format_currency(amount: float, currency_symbol: str = "£") -> str:
    """
    Format a monetary amount with proper currency display.
    
    :param amount: The monetary amount
    :param currency_symbol: Currency symbol to use
    :return: Formatted currency string
    """
    return f"{currency_symbol}{amount:.2f}"


def format_percentage(value: float) -> str:
    """
    Format a percentage value for display.
    
    :param value: The percentage value (0-100)
    :return: Formatted percentage string
    """
    return f"{value:.1f}%"


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
        return False, "Name contains invalid characters (use letters, numbers, spaces, hyphens, underscores, dots)"
    
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
    cleaned = input_str.strip().replace('£', '').replace('$', '').replace('€', '')
    
    try:
        amount = float(cleaned)
        
        if amount <= 0:
            return False, 0.0, "Amount must be positive"
        
        if amount > 999999.99:
            return False, 0.0, "Amount too large (max £999,999.99)"
        
        # Check decimal places
        if '.' in cleaned and len(cleaned.split('.')[1]) > 2:
            return False, 0.0, "Amount cannot have more than 2 decimal places"
        
        return True, round(amount, 2), ""
        
    except ValueError:
        return False, 0.0, "Invalid amount format"


def generate_expense_summary(expenses: List[Any]) -> Dict[str, Any]:
    """
    Generate summary statistics for a list of expenses.
    
    :param expenses: List of Expense objects
    :return: Dictionary with summary statistics
    """
    if not expenses:
        return {
            "total_count": 0,
            "total_amount": 0.0,
            "average_amount": 0.0,
            "largest_expense": None,
            "smallest_expense": None,
            "most_common_split": None
        }
    
    total_amount = sum(expense.amount for expense in expenses)
    amounts = [expense.amount for expense in expenses]
    split_types = [str(expense.split) for expense in expenses]
    
    # Find most common split type
    split_counts = {}
    for split_type in split_types:
        split_counts[split_type] = split_counts.get(split_type, 0) + 1
    
    most_common_split = max(split_counts.keys(), key=lambda k: split_counts[k]) if split_counts else None
    
    return {
        "total_count": len(expenses),
        "total_amount": total_amount,
        "average_amount": total_amount / len(expenses),
        "largest_expense": max(amounts),
        "smallest_expense": min(amounts),
        "most_common_split": most_common_split
    }


def format_transaction_list(transactions: List[str]) -> str:
    """
    Format a list of transactions for display.
    
    :param transactions: List of transaction strings
    :return: Formatted transaction list
    """
    if not transactions:
        return "✅ No transactions needed - everyone is settled up!"
    
    formatted = []
    for i, transaction in enumerate(transactions, 1):
        formatted.append(f"  {i}. {transaction}")
    
    return "\n".join(formatted)


class ProgressTracker:
    """Helper class to track and display progress for long operations."""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
    
    def update(self, increment: int = 1) -> None:
        """Update progress by increment amount."""
        self.current += increment
        if self.current > self.total:
            self.current = self.total
    
    def get_percentage(self) -> float:
        """Get current progress as percentage."""
        if self.total == 0:
            return 100.0
        return (self.current / self.total) * 100
    
    def is_complete(self) -> bool:
        """Check if progress is complete."""
        return self.current >= self.total
    
    def reset(self) -> None:
        """Reset progress to zero."""
        self.current = 0
