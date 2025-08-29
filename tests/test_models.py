"""
Test module for models.py - tests Person and Expense classes
"""

import pytest
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Person, Expense, is_valid_money
from split_strategies import EqualSplit, WeightsSplit, PercentSplit, ExactSplit


class TestPerson:
    """Test cases for the Person class."""

    def test_person_creation(self):
        """Test creating a person with default values."""
        person = Person("john")
        assert person.name == "john"
        assert person.balance == 0
        assert person.paid == 0
        assert person.owe == 0

    def test_person_creation_with_values(self):
        """Test creating a person with specific values."""
        person = Person("jane", balance=50.0, paid=100.0, owe=50.0)
        assert person.name == "jane"
        assert person.balance == 50.0
        assert person.paid == 100.0
        assert person.owe == 50.0

    def test_person_name_validation(self):
        """Test name validation in Person."""
        with pytest.raises(ValueError, match="Missing name"):
            person = Person("")

    def test_person_balance_validation_invalid_money(self):
        """Test balance validation with invalid monetary values."""
        person = Person("test")
        with pytest.raises(ValueError, match="Balance not valid monetary amount"):
            person.balance = 10.123  # More than 2 decimal places

    def test_person_balance_validation_valid_money(self):
        """Test balance validation with valid monetary values."""
        person = Person("test")
        person.balance = 10.12  # Exactly 2 decimal places
        assert person.balance == 10.12

        person.balance = 15  # Whole number
        assert person.balance == 15

        person.balance = 20.5  # 1 decimal place
        assert person.balance == 20.5

    def test_person_str_representation(self):
        """Test string representation of Person."""
        person = Person("alice", balance=25.50)
        assert str(person) == "Alice with balance: 25.5£"


class TestExpense:
    """Test cases for the Expense class."""

    def test_expense_creation_equal_split(self):
        """Test creating an expense with equal split."""
        expense = Expense("john", 100.0, ["john", "jane"], "equal")
        assert expense.payer == "john"
        assert expense.amount == 100.0
        assert expense.participants == ["john", "jane"]
        assert isinstance(expense.split, EqualSplit)

    def test_expense_creation_weights_split(self):
        """Test creating an expense with weights split."""
        weights = {"john": 2, "jane": 1}
        expense = Expense("john", 150.0, ["john", "jane"], "weights", weights=weights)
        assert isinstance(expense.split, WeightsSplit)
        assert expense.split.weights == weights

    def test_expense_creation_percent_split(self):
        """Test creating an expense with percent split."""
        percentages = {"john": 60, "jane": 40}
        expense = Expense(
            "john", 200.0, ["john", "jane"], "percent", percentages=percentages
        )
        assert isinstance(expense.split, PercentSplit)
        assert expense.split.percentages == percentages

    def test_expense_creation_exact_split(self):
        """Test creating an expense with exact split."""
        exact_amounts = {"john": 75.0, "jane": 25.0}
        expense = Expense(
            "john", 100.0, ["john", "jane"], "exact", exact_amounts=exact_amounts
        )
        assert isinstance(expense.split, ExactSplit)
        assert expense.split.exact_amounts == exact_amounts

    def test_expense_invalid_split_type(self):
        """Test creating an expense with invalid split type."""
        with pytest.raises(ValueError, match="Split method not valid"):
            Expense("john", 100.0, ["john", "jane"], "invalid")

    def test_expense_payer_validation(self):
        """Test payer validation in Expense."""
        expense = Expense("john", 100.0, ["john", "jane"], "equal")
        with pytest.raises(ValueError, match="Missing payer"):
            expense.payer = ""

    def test_expense_amount_validation_negative(self):
        """Test amount validation with negative values."""
        expense = Expense("john", 100.0, ["john", "jane"], "equal")
        with pytest.raises(ValueError, match="Expense must be positive"):
            expense.amount = -50.0

    def test_expense_amount_validation_invalid_money(self):
        """Test amount validation with invalid monetary values."""
        expense = Expense("john", 100.0, ["john", "jane"], "equal")
        with pytest.raises(ValueError, match="Expense not valid monetary amount"):
            expense.amount = 10.123  # More than 2 decimal places

    def test_expense_participants_validation(self):
        """Test participants validation in Expense."""
        expense = Expense("john", 100.0, ["john", "jane"], "equal")
        with pytest.raises(ValueError, match="Missing participants"):
            expense.participants = []

    def test_expense_str_representation(self):
        """Test string representation of Expense."""
        expense = Expense("alice", 60.0, ["alice", "bob"], "equal")
        expected = "60.0£ paid by Alice due for Alice and Bob with Equal split method"
        assert str(expense) == expected


class TestIsValidMoney:
    """Test cases for the is_valid_money function."""

    def test_valid_money_integers(self):
        """Test valid money with integers."""
        assert is_valid_money(100) == True
        assert is_valid_money(0) == True
        assert is_valid_money(-50) == True

    def test_valid_money_floats_one_decimal(self):
        """Test valid money with one decimal place."""
        assert is_valid_money(10.5) == True
        assert is_valid_money(99.9) == True

    def test_valid_money_floats_two_decimals(self):
        """Test valid money with two decimal places."""
        assert is_valid_money(10.99) == True
        assert is_valid_money(0.01) == True
        assert is_valid_money(999.99) == True

    def test_invalid_money_more_than_two_decimals(self):
        """Test invalid money with more than two decimal places."""
        assert is_valid_money(10.123) == False
        assert is_valid_money(99.9999) == False

    def test_invalid_money_non_numeric(self):
        """Test invalid money with non-numeric types."""
        assert is_valid_money("100") == False
        assert is_valid_money(None) == False
        assert is_valid_money([100]) == False
        assert is_valid_money({"amount": 100}) == False


if __name__ == "__main__":
    pytest.main([__file__])
