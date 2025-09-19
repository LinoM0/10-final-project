from split_strategies import EqualSplit, WeightsSplit, PercentSplit, ExactSplit, Split
from utils import is_valid_money
import inflect
import re

# Constants
MAX_NAME_LENGTH = 50
MIN_AMOUNT = 0.01
MAX_AMOUNT = 999999.99
MAX_PARTICIPANTS = 100

p = inflect.engine()


class Person:
    """
    Represents a person in the ledger with a name, balance, paid, and owed amounts.
    """

    def __init__(self, name: str, balance: float = 0, paid: float = 0, owe: float = 0):
        """
        Initialize a Person instance.
        :param name: Name of the person
        :param balance: Initial balance
        :param paid: Initial paid amount
        :param owe: Initial owed amount
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
        if not name:
            raise ValueError("Missing name")
        if not isinstance(name, str):
            raise TypeError("Name must be a string")
        if len(name.strip()) == 0:
            raise ValueError("Name cannot be empty or whitespace only")
        if len(name.strip()) > MAX_NAME_LENGTH:
            raise ValueError(f"Name too long (max {MAX_NAME_LENGTH} characters)")
        if not re.match(r"^[a-zA-Z0-9\s\-_\.]+$", name.strip()):
            raise ValueError(
                "Name contains invalid characters (use letters, numbers, spaces, hyphens, underscores, dots)"
            )
        self._name = name.strip().lower()

    @property
    def balance(self) -> float:
        """Get the person's balance."""
        return self._balance

    @balance.setter
    def balance(self, balance: float) -> None:
        if not is_valid_money(balance):
            raise ValueError("Balance not valid monetary amount (enter as x.yz£)")
        self._balance = balance

    def __str__(self) -> str:
        """Return a string representation of the person."""
        return f"{self.name.capitalize()} with balance: {self.balance}£"


class Expense:
    """
    Represents an expense in the ledger, including payer, amount, participants, and split strategy.
    """

    def __init__(
        self, payer: str, amount: float, participants: list[str], split: str, **kwargs
    ):
        """
        Initialize an Expense instance.
        :param payer: Name of the payer
        :param amount: Expense amount
        :param participants: List of participant names
        :param split: Split strategy ('equal', 'weights', 'percent', 'exact')
        :param kwargs: Additional arguments for split strategies
        """
        self.payer = payer
        self.amount = amount
        self.participants = participants
        if split == "equal":
            self.split = EqualSplit()
        elif split == "weights":
            self.split = WeightsSplit(kwargs.get("weights") or {})
        elif split == "percent":
            self.split = PercentSplit(kwargs.get("percentages") or {})
        elif split == "exact":
            self.split = ExactSplit(kwargs.get("exact_amounts") or {})
        else:
            raise ValueError("Split method not valid")

    @property
    def payer(self) -> str:
        """Get the payer's name."""
        return self._payer

    @payer.setter
    def payer(self, payer: str) -> None:
        if not payer:
            raise ValueError("Missing payer")
        self._payer = payer

    @property
    def amount(self) -> float:
        """Get the expense amount."""
        return self._amount

    @amount.setter
    def amount(self, amount: float) -> None:
        if not is_valid_money(amount):
            raise ValueError("Expense not valid monetary amount (enter as x.yz£)")
        if amount <= 0:
            raise ValueError("Expense must be positive")
        if amount > MAX_AMOUNT:
            raise ValueError(f"Expense cannot exceed {MAX_AMOUNT}£")
        self._amount = round(amount, 2)

    @property
    def participants(self) -> list[str]:
        """Get the list of participants."""
        return self._participants

    @participants.setter
    def participants(self, participants: list[str]) -> None:
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
            if not re.match(r"^[a-zA-Z0-9\s\-_\.]+$", clean_name):
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
        if not isinstance(split, (EqualSplit, WeightsSplit, PercentSplit, ExactSplit)):
            raise ValueError("Split method not valid")
        self._split = split

    def __str__(self) -> str:
        """
        Return a string representation of the expense.
        """
        participants_str = p.join([name.capitalize() for name in self.participants])
        return f"{self.amount}£ paid by {self.payer.capitalize()} due for {participants_str} with {self.split} method"
