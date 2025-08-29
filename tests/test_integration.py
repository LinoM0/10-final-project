"""
Integration tests for the entire expense splitting system
"""

import pytest
from unittest.mock import patch

from ledger import Ledger
from models import Expense
from split_strategies import WeightsSplit, PercentSplit, ExactSplit


class TestIntegration:
    """Integration tests for the complete expense splitting system."""

    def test_complete_equal_split_scenario(self):
        """Test a complete scenario with equal splits."""
        ledger = Ledger()

        # Add friends
        ledger.add_person("alice")
        ledger.add_person("bob")
        ledger.add_person("charlie")

        # Restaurant bill - Alice pays
        ledger.add_expense("alice", 150.0, ["alice", "bob", "charlie"], "equal")

        # Taxi - Bob pays
        ledger.add_expense("bob", 30.0, ["alice", "bob", "charlie"], "equal")

        # Coffee - Charlie pays
        ledger.add_expense("charlie", 18.0, ["alice", "bob", "charlie"], "equal")

        # Calculate balances
        ledger.balances()

        # Each person should owe (150+30+18)/3 = 66
        # Alice: paid 150, owes 66, balance = 84
        # Bob: paid 30, owes 66, balance = -36
        # Charlie: paid 18, owes 66, balance = -48

        assert ledger.people["alice"].balance == 84.0
        assert ledger.people["bob"].balance == -36.0
        assert ledger.people["charlie"].balance == -48.0

        # Settlement should resolve all debts
        initial_total = sum(p.balance for p in ledger.people.values())
        ledger.settle()
        final_total = sum(p.balance for p in ledger.people.values())

        # Total should remain the same (conservation of money)
        assert abs(initial_total - final_total) < 0.01

        # All individual balances should be close to 0
        for person in ledger.people.values():
            assert abs(person.balance) < 0.01

    def test_complete_mixed_split_scenario(self):
        """Test a scenario with different split strategies."""
        ledger = Ledger()

        # Add people
        ledger.add_person("alice")
        ledger.add_person("bob")
        ledger.add_person("charlie")

        # Restaurant - equal split
        ledger.add_expense("alice", 120.0, ["alice", "bob", "charlie"], "equal")

        # Grocery - percent split (alice eats more)
        percentages = {"alice": 50, "bob": 30, "charlie": 20}
        ledger.add_expense(
            "bob", 60.0, ["alice", "bob", "charlie"], "percent", percentages=percentages
        )

        # Gas - weights split (alice drives more)
        weights = {"alice": 3, "bob": 1, "charlie": 1}
        ledger.add_expense(
            "charlie", 50.0, ["alice", "bob", "charlie"], "weights", weights=weights
        )

        # Calculate and verify balances
        ledger.balances()

        # Alice: paid 120, owes (40 + 30 + 30) = 100, balance = 20
        # Bob: paid 60, owes (40 + 18 + 10) = 68, balance = -8
        # Charlie: paid 50, owes (40 + 12 + 10) = 62, balance = -12

        assert ledger.people["alice"].balance == 20.0
        assert ledger.people["bob"].balance == -8.0
        assert ledger.people["charlie"].balance == -12.0

        # Total should be conserved
        total_balance = sum(p.balance for p in ledger.people.values())
        assert abs(total_balance) < 0.01  # Should be essentially 0

    def test_exact_split_scenario(self):
        """Test scenario with exact amounts split."""
        ledger = Ledger()

        ledger.add_person("alice")
        ledger.add_person("bob")
        ledger.add_person("charlie")

        # Shared apartment utilities with exact amounts
        exact_amounts = {"alice": 45.50, "bob": 32.25, "charlie": 22.25}
        ledger.add_expense(
            "alice",
            100.0,
            ["alice", "bob", "charlie"],
            "exact",
            exact_amounts=exact_amounts,
        )

        ledger.balances()

        # Alice: paid 100, owes 45.50, balance = 54.50
        # Bob: paid 0, owes 32.25, balance = -32.25
        # Charlie: paid 0, owes 22.25, balance = -22.25

        assert ledger.people["alice"].balance == 54.50
        assert ledger.people["bob"].balance == -32.25
        assert ledger.people["charlie"].balance == -22.25

    def test_large_group_scenario(self):
        """Test scenario with a larger group."""
        ledger = Ledger()

        # Add 5 people
        people_names = ["alice", "bob", "charlie", "diana", "eve"]
        for name in people_names:
            ledger.add_person(name)

        # Big dinner - equal split
        ledger.add_expense("alice", 250.0, people_names, "equal")

        # Drinks - some people don't drink
        ledger.add_expense("bob", 80.0, ["alice", "bob", "charlie"], "equal")

        # Taxi for 3 people
        ledger.add_expense("charlie", 45.0, ["charlie", "diana", "eve"], "equal")

        ledger.balances()

        # Verify that the total balance is conserved
        total_balance = sum(p.balance for p in ledger.people.values())
        assert abs(total_balance) < 0.01

        # Settlement should work even with complex debts
        ledger.settle()

        # All balances should be settled
        for person in ledger.people.values():
            assert abs(person.balance) < 0.01

    def test_edge_case_single_person_expense(self):
        """Test edge case where expense has only one participant."""
        ledger = Ledger()

        ledger.add_person("alice")
        ledger.add_person("bob")

        # Alice buys something just for herself
        ledger.add_expense("alice", 25.0, ["alice"], "equal")

        # Bob buys something shared
        ledger.add_expense("bob", 40.0, ["alice", "bob"], "equal")

        ledger.balances()

        # Alice: paid 25, owes (25 + 20) = 45, balance = -20
        # Bob: paid 40, owes 20, balance = 20

        assert ledger.people["alice"].balance == -20.0
        assert ledger.people["bob"].balance == 20.0

    def test_rounding_precision_scenario(self):
        """Test scenario that tests rounding precision."""
        ledger = Ledger()

        ledger.add_person("alice")
        ledger.add_person("bob")
        ledger.add_person("charlie")

        # Amount that doesn't divide evenly
        ledger.add_expense("alice", 10.0, ["alice", "bob", "charlie"], "equal")

        ledger.balances()

        # 10/3 = 3.3333... for each person (preserves precision)
        for person in ledger.people.values():
            assert person.owe == 10.0 / 3

        # Alice: paid 10, owes 3.33, balance = 6.67
        # Bob: paid 0, owes 3.33, balance = -3.33
        # Charlie: paid 0, owes 3.33, balance = -3.33

        assert ledger.people["alice"].balance == 6.67
        assert ledger.people["bob"].balance == -3.33
        assert ledger.people["charlie"].balance == -3.33

        # Total should still be conserved despite rounding
        total = sum(p.balance for p in ledger.people.values())
        assert abs(total - 0.01) < 0.01  # Small rounding error acceptable

    @patch("builtins.input", side_effect=["y", "y"])  # Auto-create missing people
    def test_auto_creation_workflow(self, mock_input):
        """Test workflow with automatic person creation."""
        ledger = Ledger()

        # Start with empty ledger, add expense with new people
        ledger.add_expense("alice", 100.0, ["alice", "bob"], "equal")

        # Both people should have been created automatically
        assert "alice" in ledger.people
        assert "bob" in ledger.people
        assert len(ledger.expenses) == 1

        ledger.balances()

        # Normal split behavior should work
        assert ledger.people["alice"].balance == 50.0
        assert ledger.people["bob"].balance == -50.0

    def test_multiple_currencies_simulation(self):
        """Test simulation of multiple currencies (treating as different amounts)."""
        ledger = Ledger()

        ledger.add_person("alice")
        ledger.add_person("bob")

        # Simulate different "currencies" with different amounts
        # EUR expense (converted to base currency)
        ledger.add_expense(
            "alice", 85.50, ["alice", "bob"], "equal"
        )  # 100 EUR -> 85.50 base

        # USD expense (converted to base currency)
        ledger.add_expense(
            "bob", 92.75, ["alice", "bob"], "equal"
        )  # 100 USD -> 92.75 base

        ledger.balances()

        # With precision-first approach:
        # Expense 1: 85.50 / 2 = 42.75 each
        # Expense 2: 92.75 / 2 = 46.375 each (no intermediate rounding)
        # Total owed per person: 42.75 + 46.375 = 89.125
        # Alice: paid 85.50, owes 89.125, balance = -3.625 -> -3.62 (rounded at settlement)
        # Bob: paid 92.75, owes 89.125, balance = 3.625 -> 3.62 (rounded at settlement)

        assert ledger.people["alice"].balance == -3.62
        assert ledger.people["bob"].balance == 3.62

    def test_stress_test_many_expenses(self):
        """Stress test with many small expenses."""
        ledger = Ledger()

        # Add people
        for i in range(5):
            ledger.add_person(f"person{i}")

        participants = [f"person{i}" for i in range(5)]

        # Add many small expenses
        for i in range(20):
            payer = f"person{i % 5}"
            amount = (i + 1) * 5.0  # 5, 10, 15, ..., 100
            ledger.add_expense(payer, amount, participants, "equal")

        ledger.balances()

        # Verify conservation of money
        total_paid = sum(p.paid for p in ledger.people.values())
        total_owed = sum(p.owe for p in ledger.people.values())
        assert abs(total_paid - total_owed) < 0.01

        # Settlement should work
        ledger.settle()

        # All balances should be settled
        for person in ledger.people.values():
            assert abs(person.balance) < 0.01


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_invalid_split_strategies(self):
        """Test that invalid split strategies are handled properly."""
        with pytest.raises(ValueError, match="Split method not valid"):
            Expense("alice", 100.0, ["alice", "bob"], "invalid_split")

    def test_empty_participant_list(self):
        """Test handling of empty participant list."""
        with pytest.raises(ValueError, match="Missing participants"):
            expense = Expense("alice", 100.0, ["alice"], "equal")
            expense.participants = []

    def test_negative_expense_amount(self):
        """Test handling of negative expense amounts."""
        with pytest.raises(ValueError, match="Expense must be positive"):
            expense = Expense("alice", 100.0, ["alice"], "equal")
            expense.amount = -50.0

    def test_weights_split_error_cases(self):
        """Test error cases for weights split."""
        # Missing weights for participants
        with pytest.raises(
            ValueError, match="Weights must be provided for all participants"
        ):
            split = WeightsSplit({"alice": 2})
            split.compute_shares(100.0, ["alice", "bob"])

        # Zero total weight
        with pytest.raises(ValueError, match="Total weight must be greater than zero"):
            split = WeightsSplit({"alice": 0, "bob": 0})
            split.compute_shares(100.0, ["alice", "bob"])

    def test_percent_split_error_cases(self):
        """Test error cases for percent split."""
        # Percentages don't sum to 100
        with pytest.raises(ValueError, match="Percentages must sum to 100%"):
            split = PercentSplit({"alice": 60, "bob": 30})  # Sum is 90
            split.compute_shares(100.0, ["alice", "bob"])

    def test_exact_split_error_cases(self):
        """Test error cases for exact split."""
        # Amounts don't sum to total
        with pytest.raises(
            ValueError, match="Exact amounts must sum to the total amount"
        ):
            split = ExactSplit({"alice": 60.0, "bob": 30.0})  # Sum is 90, not 100
            split.compute_shares(100.0, ["alice", "bob"])


if __name__ == "__main__":
    pytest.main([__file__])
