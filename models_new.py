"""
Data models for the Expense Splitting Calculator application.

This module defines the core data structures: Person and Expense classes,
along with validation functions for monetary values.
"""

import re
import inflect
from split_strategies import EqualSplit, WeightsSplit, PercentSplit, ExactSplit, Split
from constants import (
    MAX_NAME_LENGTH,
    NAME_PATTERN,
    MAX_AMOUNT,
    MAX_PARTICIPANTS,
    ROUNDING_PRECISION,
)

# Initialize inflect engine for natural language formatting
p = inflect.engine()


def is_valid_money(value) -> bool:
    """
    Check if a value represents a valid monetary amount.

    Args:
        value: Value to validate (any type)

    Returns:
        True if valid monetary amount, False otherwise
    """
    if not isinstance(value, (int, float)):
        return False

    # Check for infinite values and NaN
    if not (float("-inf") < value < float("inf")) or value != value:
        return False

    # Validate decimal places precision
    value_str = f"{value:.10f}".rstrip("0").rstrip(".")
    if "." in value_str:
        decimals = value_str.split(".")[1]
        return len(decimals) <= ROUNDING_PRECISION

    return True


class Person:
    """
    Represents a person in the expense ledger.

    Attributes:
        name (str): Person's name (cleaned and normalized)
        balance (float): Current balance (paid - owed)
        paid (float): Total amount paid by this person
        owe (float): Total amount owed by this person
    """

    def __init__(self, name: str, balance: float = 0, paid: float = 0, owe: float = 0):
        """
        Initialize a Person instance.

        Args:
            name: Person's name
            balance: Initial balance
            paid: Initial paid amount
            owe: Initial owed amount
        """
        self.name = name
        self.balance = balance
        self.paid = paid
        self.owe = owe

    @property
    def name(self) -> str:
        """Get the person's name."""
        return self._name

    @name.setter
    def name(self, name: str) -> None:
        """Set and validate the person's name."""
        if not name:
            raise ValueError("Missing name")
        if not isinstance(name, str):
            raise TypeError("Name must be a string")

        cleaned_name = name.strip()
        if not cleaned_name:
            raise ValueError("Name cannot be empty or whitespace only")
        if len(cleaned_name) > MAX_NAME_LENGTH:
            raise ValueError(f"Name too long (max {MAX_NAME_LENGTH} characters)")
        if not re.match(NAME_PATTERN, cleaned_name):
            raise ValueError(
                "Name contains invalid characters (use letters, numbers, spaces, hyphens, underscores, dots)"
            )

        self._name = cleaned_name.lower()

    @property
    def balance(self) -> float:
        """Get the person's balance."""
        return self._balance

    @balance.setter
    def balance(self, balance: float) -> None:
        """Set and validate the person's balance."""
        if not is_valid_money(balance):
            raise ValueError("Balance not valid monetary amount")
        self._balance = balance

    def __str__(self) -> str:
        """Return a string representation of the person."""
        return f"{self.name.capitalize()} with balance: {self.balance:.{ROUNDING_PRECISION}f}£"


class Expense:
    """
    Represents an expense in the ledger with split strategy.

    Attributes:
        payer (str): Name of the person who paid
        amount (float): Expense amount
        participants (list[str]): List of people involved in the expense
        split (Split): Strategy object for splitting the expense
    """

    def __init__(
        self, payer: str, amount: float, participants: list[str], split: str, **kwargs
    ):
        """
        Initialize an Expense instance.

        Args:
            payer: Name of the person who paid
            amount: Expense amount
            participants: List of participant names
            split: Split strategy type ('equal', 'weights', 'percent', 'exact')
            **kwargs: Additional arguments for split strategies
        """
        self.payer = payer
        self.amount = amount
        self.participants = participants
        self._set_split_strategy(split, kwargs)

    def _set_split_strategy(self, split: str, kwargs: dict) -> None:
        """Set the split strategy based on the split type."""
        split_strategies = {
            "equal": lambda: EqualSplit(),
            "weights": lambda: WeightsSplit(kwargs.get("weights") or {}),
            "percent": lambda: PercentSplit(kwargs.get("percentages") or {}),
            "exact": lambda: ExactSplit(kwargs.get("exact_amounts") or {}),
        }

        if split not in split_strategies:
            raise ValueError("Split method not valid")

        self.split = split_strategies[split]()

    @property
    def payer(self) -> str:
        """Get the payer's name."""
        return self._payer

    @payer.setter
    def payer(self, payer: str) -> None:
        """Set and validate the payer's name."""
        if not payer:
            raise ValueError("Missing payer")
        self._payer = payer

    @property
    def amount(self) -> float:
        """Get the expense amount."""
        return self._amount

    @amount.setter
    def amount(self, amount: float) -> None:
        """Set and validate the expense amount."""
        if not is_valid_money(amount):
            raise ValueError("Expense not valid monetary amount")
        if amount <= 0:
            raise ValueError("Expense must be positive")
        if amount > MAX_AMOUNT:
            raise ValueError(f"Expense cannot exceed {MAX_AMOUNT}£")
        self._amount = round(amount, ROUNDING_PRECISION)

    @property
    def participants(self) -> list[str]:
        """Get the list of participants."""
        return self._participants

    @participants.setter
    def participants(self, participants: list[str]) -> None:
        """Set and validate the participants list."""
        if not participants:
            raise ValueError("Missing participants")
        if not isinstance(participants, list):
            raise TypeError("Participants must be a list")
        if len(participants) > MAX_PARTICIPANTS:
            raise ValueError(f"Too many participants (max {MAX_PARTICIPANTS})")

        # Clean and validate each participant name
        clean_participants = []
        for participant in participants:
            if not isinstance(participant, str):
                raise TypeError("All participant names must be strings")

            clean_name = participant.strip().lower()
            if not clean_name:
                raise ValueError("Participant names cannot be empty")
            if len(clean_name) > MAX_NAME_LENGTH:
                raise ValueError(
                    f"Participant name too long (max {MAX_NAME_LENGTH} characters)"
                )
            if not re.match(NAME_PATTERN, clean_name):
                raise ValueError("Participant name contains invalid characters")

            clean_participants.append(clean_name)

        if len(set(clean_participants)) != len(clean_participants):
            raise ValueError("Duplicate participants found")

        self._participants = clean_participants

    @property
    def split(self) -> Split:
        """Get the split strategy object."""
        return self._split

    @split.setter
    def split(self, split: Split) -> None:
        """Set and validate the split strategy."""
        if not isinstance(split, (EqualSplit, WeightsSplit, PercentSplit, ExactSplit)):
            raise ValueError("Split method not valid")
        self._split = split

    def __str__(self) -> str:
        """Return a string representation of the expense."""
        participants_str = p.join([name.capitalize() for name in self.participants])
        return (
            f"{self.amount:.{ROUNDING_PRECISION}f}£ paid by {self.payer.capitalize()} "
            f"due for {participants_str} with {self.split} method"
        )
