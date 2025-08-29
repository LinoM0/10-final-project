"""
Test module for ledger.py - tests the Ledger class and all its methods
"""

import pytest
from io import StringIO
from unittest.mock import patch

from ledger import Ledger
from models import Person, Expense


class TestLedger:
    """Test cases for the Ledger class."""

    def test_ledger_initialization_empty(self):
        """Test ledger initialization with no arguments."""
        ledger = Ledger()
        assert ledger.people == {}
        assert ledger.expenses == []

    def test_ledger_initialization_with_data(self):
        """Test ledger initialization with existing data."""
        people = {"alice": Person("alice", 50.0)}
        expenses = [Expense("alice", 100.0, ["alice", "bob"], "equal")]
        ledger = Ledger(people=people, expenses=expenses)
        assert ledger.people == people
        assert ledger.expenses == expenses

    def test_add_person_new(self):
        """Test adding a new person to the ledger."""
        ledger = Ledger()
        ledger.add_person("alice", balance=25.0, paid=100.0, owe=75.0)

        assert "alice" in ledger.people
        person = ledger.people["alice"]
        assert person.name == "alice"
        assert person.balance == 25.0
        assert person.paid == 100.0
        assert person.owe == 75.0

    def test_add_person_existing(self):
        """Test adding an existing person to the ledger."""
        ledger = Ledger()
        ledger.add_person("alice")

        # Capture print output
        with patch("sys.stdout", new=StringIO()) as fake_output:
            ledger.add_person("alice")
            output = fake_output.getvalue()

        assert "Person alice already exists!" in output
        assert len(ledger.people) == 1  # Should still be only one person

    def test_add_person_name_cleaning(self):
        """Test that person names are cleaned (stripped and lowercased)."""
        ledger = Ledger()
        ledger.add_person("  ALICE  ")

        assert "alice" in ledger.people
        assert "  ALICE  " not in ledger.people

    @patch("builtins.input", return_value="y")
    def test_add_expense_create_missing_payer(self, mock_input):
        """Test adding expense with missing payer (user chooses to create)."""
        ledger = Ledger()
        ledger.add_person("bob")

        ledger.add_expense("alice", 100.0, ["alice", "bob"], "equal")

        assert "alice" in ledger.people
        assert len(ledger.expenses) == 1
        assert ledger.people["alice"].paid == 100.0

    @patch("builtins.input", return_value="n")
    def test_add_expense_reject_missing_payer(self, mock_input):
        """Test adding expense with missing payer (user rejects creation)."""
        ledger = Ledger()
        ledger.add_person("bob")

        with pytest.raises(IndexError, match="Person Alice does not exist"):
            ledger.add_expense("alice", 100.0, ["alice", "bob"], "equal")

    @patch("builtins.input", return_value="y")
    def test_add_expense_create_missing_participant(self, mock_input):
        """Test adding expense with missing participant (user chooses to create)."""
        ledger = Ledger()
        ledger.add_person("alice")

        ledger.add_expense("alice", 100.0, ["alice", "bob"], "equal")

        assert "bob" in ledger.people
        assert len(ledger.expenses) == 1

    @patch("builtins.input", return_value="n")
    def test_add_expense_reject_missing_participant(self, mock_input):
        """Test adding expense with missing participant (user rejects creation)."""
        ledger = Ledger()
        ledger.add_person("alice")

        with pytest.raises(IndexError, match="Person Bob does not exist"):
            ledger.add_expense("alice", 100.0, ["alice", "bob"], "equal")

    def test_add_expense_equal_split(self):
        """Test adding expense with equal split."""
        ledger = Ledger()
        ledger.add_person("alice")
        ledger.add_person("bob")

        ledger.add_expense("alice", 100.0, ["alice", "bob"], "equal")

        assert len(ledger.expenses) == 1
        expense = ledger.expenses[0]
        assert expense.payer == "alice"
        assert expense.amount == 100.0
        assert expense.participants == ["alice", "bob"]
        assert ledger.people["alice"].paid == 100.0

    def test_add_expense_percent_split(self):
        """Test adding expense with percent split."""
        ledger = Ledger()
        ledger.add_person("alice")
        ledger.add_person("bob")

        percentages = {"alice": 60, "bob": 40}
        ledger.add_expense(
            "alice", 100.0, ["alice", "bob"], "percent", percentages=percentages
        )

        assert len(ledger.expenses) == 1
        expense = ledger.expenses[0]
        from split_strategies import PercentSplit
        assert isinstance(expense.split, PercentSplit)
        assert expense.split.percentages == percentages

    def test_balances_calculation(self):
        """Test balance calculation after adding expenses."""
        ledger = Ledger()
        ledger.add_person("alice")
        ledger.add_person("bob")

        # Alice pays 100, split equally between alice and bob
        ledger.add_expense("alice", 100.0, ["alice", "bob"], "equal")
        ledger.balances()

        # Alice paid 100, owes 50, balance = 50
        # Bob paid 0, owes 50, balance = -50
        assert ledger.people["alice"].balance == 50.0
        assert ledger.people["bob"].balance == -50.0
        assert ledger.people["alice"].paid == 100.0
        assert ledger.people["alice"].owe == 50.0
        assert ledger.people["bob"].paid == 0.0
        assert ledger.people["bob"].owe == 50.0

    def test_balances_multiple_expenses(self):
        """Test balance calculation with multiple expenses."""
        ledger = Ledger()
        ledger.add_person("alice")
        ledger.add_person("bob")

        # Alice pays 100, split equally
        ledger.add_expense("alice", 100.0, ["alice", "bob"], "equal")
        # Bob pays 60, split equally
        ledger.add_expense("bob", 60.0, ["alice", "bob"], "equal")
        ledger.balances()

        # Alice: paid 100, owes 80 (50+30), balance = 20
        # Bob: paid 60, owes 80 (50+30), balance = -20
        assert ledger.people["alice"].balance == 20.0
        assert ledger.people["bob"].balance == -20.0

    def test_balances_reset_owe(self):
        """Test that balances() resets owe amounts before calculation."""
        ledger = Ledger()
        ledger.add_person("alice", owe=999.0)  # Start with high owe
        ledger.add_person("bob")

        ledger.add_expense("alice", 100.0, ["alice", "bob"], "equal")
        ledger.balances()

        # Should reset to 50, not add to 999
        assert ledger.people["alice"].owe == 50.0

    def test_settle_simple(self):
        """Test simple settlement between two people."""
        ledger = Ledger()
        ledger.add_person("alice", balance=50.0)
        ledger.add_person("bob", balance=-50.0)

        with patch("sys.stdout", new=StringIO()) as fake_output:
            ledger.settle()
            output = fake_output.getvalue()

        assert "Bob → Alice: 50.0£" in output
        assert ledger.people["alice"].balance == 0.0
        assert ledger.people["bob"].balance == 0.0

    def test_settle_multiple_people(self):
        """Test settlement with multiple people."""
        ledger = Ledger()
        ledger.add_person("alice", balance=80.0)
        ledger.add_person("bob", balance=-30.0)
        ledger.add_person("charlie", balance=-50.0)

        with patch("sys.stdout", new=StringIO()) as fake_output:
            ledger.settle()
            output = fake_output.getvalue()

        # Should have transfers that balance out
        lines = output.strip().split("\n")
        assert len(lines) == 2  # Should be exactly 2 transfers
        assert "→" in output  # Should contain transfer arrows

    def test_settle_no_imbalance(self):
        """Test settlement when everyone has zero balance."""
        ledger = Ledger()
        ledger.add_person("alice", balance=0.0)
        ledger.add_person("bob", balance=0.0)

        with patch("sys.stdout", new=StringIO()) as fake_output:
            ledger.settle()
            output = fake_output.getvalue()

        assert output.strip() == ""  # No output for balanced ledger

    def test_list_expenses_empty(self):
        """Test listing expenses when there are none."""
        ledger = Ledger()

        with patch("sys.stdout", new=StringIO()) as fake_output:
            ledger.list_expenses()
            output = fake_output.getvalue()

        assert "No expenses recorded." in output

    def test_list_expenses_with_data(self):
        """Test listing expenses when there are some."""
        ledger = Ledger()
        ledger.add_person("alice")
        ledger.add_person("bob")
        ledger.add_expense("alice", 100.0, ["alice", "bob"], "equal")

        with patch("sys.stdout", new=StringIO()) as fake_output:
            ledger.list_expenses()
            output = fake_output.getvalue()

        assert "Expenses:" in output
        assert "100.0£ paid by Alice" in output
        assert "Equal split" in output

    def test_list_balances_empty(self):
        """Test listing balances when there are no people."""
        ledger = Ledger()

        with patch("sys.stdout", new=StringIO()) as fake_output:
            ledger.list_balances()
            output = fake_output.getvalue()

        assert "No people in ledger." in output

    def test_list_balances_with_data(self):
        """Test listing balances when there are people."""
        ledger = Ledger()
        ledger.add_person("alice", balance=50.0)
        ledger.add_person("bob", balance=-30.0)

        with patch("sys.stdout", new=StringIO()) as fake_output:
            ledger.list_balances()
            output = fake_output.getvalue()

        assert "People:" in output
        assert "Alice with balance: 50.0£" in output
        assert "Bob with balance: -30.0£" in output

    def test_list_balances_sorted(self):
        """Test that balances are listed in descending order."""
        ledger = Ledger()
        ledger.add_person("alice", balance=-10.0)
        ledger.add_person("bob", balance=50.0)
        ledger.add_person("charlie", balance=20.0)

        with patch("sys.stdout", new=StringIO()) as fake_output:
            ledger.list_balances()
            output = fake_output.getvalue()

        lines = output.strip().split("\n")[1:]  # Skip "People:" line
        # Should be sorted: Bob (50), Charlie (20), Alice (-10)
        assert "Bob" in lines[0]
        assert "Charlie" in lines[1]
        assert "Alice" in lines[2]

    def test_str_representation(self):
        """Test string representation of ledger."""
        ledger = Ledger()
        ledger.add_person("alice", balance=25.0)
        ledger.add_person("bob", balance=-25.0)
        ledger.add_expense("alice", 50.0, ["alice", "bob"], "equal")

        result = str(ledger)

        assert "People:" in result
        assert "Expenses:" in result
        assert "Alice with balance: 25.0£" in result
        assert "50.0£ paid by Alice" in result

    def test_integration_full_workflow(self):
        """Test a complete workflow from adding people to settlement."""
        ledger = Ledger()

        # Add people
        ledger.add_person("alice")
        ledger.add_person("bob")
        ledger.add_person("charlie")

        # Add expenses
        ledger.add_expense("alice", 120.0, ["alice", "bob", "charlie"], "equal")
        ledger.add_expense("bob", 60.0, ["alice", "bob"], "equal")

        # Calculate balances
        ledger.balances()

        # Alice: paid 120, owes 70 (40+30), balance = 50
        # Bob: paid 60, owes 70 (40+30), balance = -10
        # Charlie: paid 0, owes 40, balance = -40
        assert ledger.people["alice"].balance == 50.0
        assert ledger.people["bob"].balance == -10.0
        assert ledger.people["charlie"].balance == -40.0

        # Settlement should balance everyone
        ledger.settle()

        # All balances should be 0 or very close to 0 (accounting for rounding)
        assert abs(ledger.people["alice"].balance) < 0.01
        assert abs(ledger.people["bob"].balance) < 0.01
        assert abs(ledger.people["charlie"].balance) < 0.01


if __name__ == "__main__":
    pytest.main([__file__])
