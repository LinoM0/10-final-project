"""
Ledger management for the Expense Splitting Calculator application.

This module provides the main Ledger class that manages people and expenses,
performs balance calculations, and handles debt settlement.
"""

import re
from models import Person, Expense
from constants import (
    MAX_NAME_LENGTH,
    NAME_PATTERN,
    MAX_AMOUNT,
    MAX_PEOPLE,
    SETTLEMENT_TOLERANCE,
    ROUNDING_PRECISION,
)


class Ledger:
    """
    Main ledger class for managing people and expenses.

    Handles adding people and expenses, calculating balances,
    and generating optimal debt settlement transactions.

    Attributes:
        people (dict): Dictionary mapping names to Person objects
        expenses (list): List of Expense objects
    """

    def __init__(self, people=None, expenses=None):
        """
        Initialize a Ledger instance.

        Args:
            people: Optional dictionary of people (name -> Person)
            expenses: Optional list of Expense objects
        """
        self.people: dict[str, Person] = people if people is not None else {}
        self.expenses: list[Expense] = expenses if expenses is not None else []

    def add_person(
        self, name: str, balance: float = 0, paid: float = 0, owe: float = 0
    ) -> None:
        """
        Add a person to the ledger if not already present.

        Args:
            name: Person's name
            balance: Initial balance
            paid: Initial paid amount
            owe: Initial owed amount

        Raises:
            TypeError: If name is not a string
            ValueError: If name is invalid or ledger is full
        """
        if not isinstance(name, str):
            raise TypeError("Name must be a string")

        name_clean = name.strip().lower()
        if not name_clean:
            raise ValueError("Name cannot be empty")

        if len(name_clean) > MAX_NAME_LENGTH:
            raise ValueError(f"Name too long (max {MAX_NAME_LENGTH} characters)")

        if not re.match(NAME_PATTERN, name_clean):
            raise ValueError("Name contains invalid characters")

        if len(self.people) >= MAX_PEOPLE:
            raise ValueError(f"Cannot add more people (max {MAX_PEOPLE})")

        if name_clean in self.people:
            print(f"Person {name_clean} already exists!")
            return

        self.people[name_clean] = Person(name_clean, balance, paid, owe)

    def add_expense(
        self, payer: str, amount: float, participants: list[str], split: str, **kwargs
    ) -> None:
        """
        Add an expense to the ledger with comprehensive validation.

        Args:
            payer: Name of the person who paid
            amount: Expense amount
            participants: List of participant names
            split: Split strategy ('equal', 'weights', 'percent', 'exact')
            **kwargs: Additional arguments for split strategies

        Raises:
            TypeError: If arguments have wrong types
            ValueError: If expense parameters are invalid
            IndexError: If person creation is rejected by user
        """
        # Type validation
        if not isinstance(payer, str):
            raise TypeError("Payer must be a string")
        if not isinstance(participants, list):
            raise TypeError("Participants must be a list")
        if not isinstance(amount, (int, float)):
            raise TypeError("Amount must be a number")

        # Value validation
        if not payer or not payer.strip():
            raise ValueError("Payer name cannot be empty")
        if not participants:
            raise ValueError("Participants list cannot be empty")
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if amount > MAX_AMOUNT:
            raise ValueError(f"Amount cannot exceed {MAX_AMOUNT}£")

        # Clean names
        payer_clean = payer.strip().lower()
        participants_clean = [p.strip().lower() for p in participants if p.strip()]

        if not participants_clean:
            raise ValueError("No valid participants after cleaning names")

        # Ensure payer exists (with user interaction)
        if payer_clean not in self.people:
            answer = input(
                f"Person {payer.capitalize()} does not exist. Create? (y/n) "
            )
            if answer.lower() == "y":
                self.add_person(payer)
            else:
                raise IndexError(
                    f"Person {payer.capitalize()} does not exist. Create them first."
                )

        # Ensure all participants exist (with user interaction)
        for participant in participants_clean:
            if participant not in self.people:
                answer = input(
                    f"Person {participant.capitalize()} does not exist. Create? (y/n) "
                )
                if answer.lower() == "y":
                    self.add_person(participant)
                else:
                    raise IndexError(
                        f"Person {participant.capitalize()} does not exist. Create them first."
                    )

        # Create and add expense
        expense = Expense(payer_clean, amount, participants_clean, split, **kwargs)
        self.expenses.append(expense)
        self.people[expense.payer].paid += expense.amount

    def balances(self) -> None:
        """
        Calculate and update each person's balance based on expenses.

        Resets all owe amounts and recalculates them based on current expenses.
        Balance = paid - owed for each person.
        """
        # Reset owe amounts for all people
        for person in self.people.values():
            person.owe = 0

        # Calculate owed amounts from expenses
        for expense in self.expenses:
            shares = expense.split.compute_shares(expense.amount, expense.participants)
            for participant, share in shares.items():
                self.people[participant].owe += share

        # Update balance for each person
        for person in self.people.values():
            person.balance = round(person.paid - person.owe, ROUNDING_PRECISION)

    def settle(self) -> None:
        """
        Generate and print optimal debt settlement transactions.

        Uses a greedy algorithm to minimize the number of transactions
        needed to settle all debts. Matches the largest creditor with
        the largest debtor iteratively.
        """
        # Separate creditors (positive balance) and debtors (negative balance)
        creditors = {p.name: p for p in self.people.values() if p.balance > 0}
        debtors = {p.name: p for p in self.people.values() if p.balance < 0}

        # Continue until all significant balances are settled
        while (
            creditors
            and debtors
            and max(p.balance for p in creditors.values()) > SETTLEMENT_TOLERANCE
        ):
            # Find the person owed the most and person who owes the most
            max_creditor = max(creditors.values(), key=lambda p: p.balance)
            max_debtor = min(debtors.values(), key=lambda p: p.balance)

            # Calculate transfer amount (limited by smaller of the two balances)
            transfer_amount = round(
                min(max_creditor.balance, abs(max_debtor.balance)), ROUNDING_PRECISION
            )

            # Print the transaction
            print(
                f"{max_debtor.name.capitalize()} → {max_creditor.name.capitalize()}: "
                f"{transfer_amount:.{ROUNDING_PRECISION}f}£"
            )

            # Update balances
            max_creditor.balance = round(
                max_creditor.balance - transfer_amount, ROUNDING_PRECISION
            )
            max_debtor.balance = round(
                max_debtor.balance + transfer_amount, ROUNDING_PRECISION
            )

            # Remove people with negligible balances
            if abs(max_creditor.balance) <= SETTLEMENT_TOLERANCE:
                del creditors[max_creditor.name]
            if abs(max_debtor.balance) <= SETTLEMENT_TOLERANCE:
                del debtors[max_debtor.name]

        # Clean up any remaining small balances due to rounding
        for person in self.people.values():
            if abs(person.balance) <= SETTLEMENT_TOLERANCE:
                person.balance = 0.0

    def list_expenses(self) -> None:
        """Print all expenses in the ledger."""
        if not self.expenses:
            print("No expenses recorded.")
            return

        expenses_str = "\n".join(str(expense) for expense in self.expenses)
        print(f"Expenses:\n{expenses_str}")

    def list_balances(self) -> None:
        """Print all people and their balances, sorted by balance descending."""
        if not self.people:
            print("No people in ledger.")
            return

        sorted_people = sorted(
            self.people.values(), key=lambda p: p.balance, reverse=True
        )
        people_str = "\n".join(str(person) for person in sorted_people)
        print(f"People:\n{people_str}")

    def __str__(self) -> str:
        """Return a string representation of the entire ledger."""
        people_str = "\n".join(str(person) for person in self.people.values())
        expenses_str = "\n".join(str(expense) for expense in self.expenses)
        return f"People:\n{people_str}\n\nExpenses:\n{expenses_str}"
