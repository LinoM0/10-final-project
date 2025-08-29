"""
Test module for split_strategies.py - tests all split strategy classes
"""

import pytest
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from split_strategies import Split, EqualSplit, WeightsSplit, PercentSplit, ExactSplit


class TestSplit:
    """Test cases for the abstract Split base class."""

    def test_split_not_implemented(self):
        """Test that Split.compute_shares raises NotImplementedError."""
        split = Split()
        with pytest.raises(
            NotImplementedError, match="Subclasses must implement compute_shares"
        ):
            split.compute_shares(100.0, ["alice", "bob"])


class TestEqualSplit:
    """Test cases for the EqualSplit class."""

    def test_equal_split_two_participants(self):
        """Test equal split with two participants."""
        split = EqualSplit()
        result = split.compute_shares(100.0, ["alice", "bob"])
        expected = {"alice": 50.0, "bob": 50.0}
        assert result == expected

    def test_equal_split_three_participants(self):
        """Test equal split with three participants."""
        split = EqualSplit()
        result = split.compute_shares(99.0, ["alice", "bob", "charlie"])
        expected = {"alice": 33.0, "bob": 33.0, "charlie": 33.0}
        assert result == expected

    def test_equal_split_odd_amount(self):
        """Test equal split with odd amount that doesn't divide evenly."""
        split = EqualSplit()
        result = split.compute_shares(10.0, ["alice", "bob", "charlie"])
        expected = {"alice": 10.0 / 3, "bob": 10.0 / 3, "charlie": 10.0 / 3}
        assert result == expected

    def test_equal_split_single_participant(self):
        """Test equal split with single participant."""
        split = EqualSplit()
        result = split.compute_shares(100.0, ["alice"])
        expected = {"alice": 100.0}
        assert result == expected

    def test_equal_split_str_representation(self):
        """Test string representation of EqualSplit."""
        split = EqualSplit()
        assert str(split) == "Equal split"


class TestWeightsSplit:
    """Test cases for the WeightsSplit class."""

    def test_weights_split_initialization(self):
        """Test WeightsSplit initialization."""
        weights = {"alice": 2, "bob": 1}
        split = WeightsSplit(weights)
        assert split.weights == weights

    def test_weights_split_initialization_empty(self):
        """Test WeightsSplit initialization with no weights."""
        split = WeightsSplit()
        assert split.weights == {}

    def test_weights_split_basic(self):
        """Test basic weights split calculation."""
        weights = {"alice": 2, "bob": 1}
        split = WeightsSplit(weights)
        result = split.compute_shares(90.0, ["alice", "bob"])
        expected = {"alice": 60.0, "bob": 30.0}  # 2:1 ratio
        assert result == expected

    def test_weights_split_three_participants(self):
        """Test weights split with three participants."""
        weights = {"alice": 3, "bob": 2, "charlie": 1}
        split = WeightsSplit(weights)
        result = split.compute_shares(120.0, ["alice", "bob", "charlie"])
        expected = {"alice": 60.0, "bob": 40.0, "charlie": 20.0}  # 3:2:1 ratio
        assert result == expected

    def test_weights_split_passed_weights(self):
        """Test weights split with weights passed to compute_shares."""
        split = WeightsSplit()  # No initial weights
        weights = {"alice": 1, "bob": 2}
        result = split.compute_shares(90.0, ["alice", "bob"], weights=weights)
        expected = {"alice": 30.0, "bob": 60.0}  # 1:2 ratio
        assert result == expected

    def test_weights_split_missing_participants(self):
        """Test weights split with missing participant weights."""
        weights = {"alice": 2}  # Missing bob
        split = WeightsSplit(weights)
        with pytest.raises(
            ValueError, match="Weights must be provided for all participants"
        ):
            split.compute_shares(100.0, ["alice", "bob"])

    def test_weights_split_zero_total_weight(self):
        """Test weights split with zero total weight."""
        weights = {"alice": 0, "bob": 0}
        split = WeightsSplit(weights)
        with pytest.raises(ValueError, match="Total weight must be greater than zero"):
            split.compute_shares(100.0, ["alice", "bob"])

    def test_weights_split_key_cleaning(self):
        """Test weights split with key cleaning (capitalized keys)."""
        weights = {"Alice": 2, "Bob": 1}  # Capitalized keys
        split = WeightsSplit(weights)
        result = split.compute_shares(90.0, ["alice", "bob"])  # lowercase participants
        expected = {"alice": 60.0, "bob": 30.0}
        assert result == expected

    def test_weights_split_str_representation(self):
        """Test string representation of WeightsSplit."""
        split = WeightsSplit()
        assert str(split) == "Weights split"


class TestPercentSplit:
    """Test cases for the PercentSplit class."""

    def test_percent_split_initialization(self):
        """Test PercentSplit initialization."""
        percentages = {"alice": 60, "bob": 40}
        split = PercentSplit(percentages)
        assert split.percentages == percentages

    def test_percent_split_initialization_empty(self):
        """Test PercentSplit initialization with no percentages."""
        split = PercentSplit()
        assert split.percentages == {}

    def test_percent_split_basic(self):
        """Test basic percent split calculation."""
        percentages = {"alice": 60, "bob": 40}
        split = PercentSplit(percentages)
        result = split.compute_shares(100.0, ["alice", "bob"])
        expected = {"alice": 60.0, "bob": 40.0}
        assert result == expected

    def test_percent_split_three_participants(self):
        """Test percent split with three participants."""
        percentages = {"alice": 50, "bob": 30, "charlie": 20}
        split = PercentSplit(percentages)
        result = split.compute_shares(200.0, ["alice", "bob", "charlie"])
        expected = {"alice": 100.0, "bob": 60.0, "charlie": 40.0}
        assert result == expected

    def test_percent_split_passed_percentages(self):
        """Test percent split with percentages passed to compute_shares."""
        split = PercentSplit()  # No initial percentages
        percentages = {"alice": 75, "bob": 25}
        result = split.compute_shares(80.0, ["alice", "bob"], percentages=percentages)
        expected = {"alice": 60.0, "bob": 20.0}
        assert result == expected

    def test_percent_split_missing_participants(self):
        """Test percent split with missing participant percentages."""
        percentages = {"alice": 100}  # Missing bob
        split = PercentSplit(percentages)
        with pytest.raises(
            ValueError, match="Percentages must be provided for all participants"
        ):
            split.compute_shares(100.0, ["alice", "bob"])

    def test_percent_split_not_100_percent(self):
        """Test percent split with percentages not summing to 100."""
        percentages = {"alice": 60, "bob": 30}  # Sum is 90, not 100
        split = PercentSplit(percentages)
        with pytest.raises(ValueError, match="Percentages must sum to 100%"):
            split.compute_shares(100.0, ["alice", "bob"])

    def test_percent_split_key_cleaning(self):
        """Test percent split with key cleaning (capitalized keys)."""
        percentages = {"Alice": 70, "Bob": 30}  # Capitalized keys
        split = PercentSplit(percentages)
        result = split.compute_shares(100.0, ["alice", "bob"])  # lowercase participants
        expected = {"alice": 70.0, "bob": 30.0}
        assert result == expected

    def test_percent_split_str_representation(self):
        """Test string representation of PercentSplit."""
        split = PercentSplit()
        assert str(split) == "Percent split"


class TestExactSplit:
    """Test cases for the ExactSplit class."""

    def test_exact_split_initialization(self):
        """Test ExactSplit initialization."""
        exact_amounts = {"alice": 60.0, "bob": 40.0}
        split = ExactSplit(exact_amounts)
        assert split.exact_amounts == exact_amounts

    def test_exact_split_initialization_empty(self):
        """Test ExactSplit initialization with no exact amounts."""
        split = ExactSplit()
        assert split.exact_amounts == {}

    def test_exact_split_basic(self):
        """Test basic exact split calculation."""
        exact_amounts = {"alice": 60.0, "bob": 40.0}
        split = ExactSplit(exact_amounts)
        result = split.compute_shares(100.0, ["alice", "bob"])
        expected = {"alice": 60.0, "bob": 40.0}
        assert result == expected

    def test_exact_split_three_participants(self):
        """Test exact split with three participants."""
        exact_amounts = {"alice": 50.0, "bob": 30.0, "charlie": 20.0}
        split = ExactSplit(exact_amounts)
        result = split.compute_shares(100.0, ["alice", "bob", "charlie"])
        expected = {"alice": 50.0, "bob": 30.0, "charlie": 20.0}
        assert result == expected

    def test_exact_split_passed_amounts(self):
        """Test exact split with amounts passed to compute_shares."""
        split = ExactSplit()  # No initial amounts
        exact_amounts = {"alice": 75.0, "bob": 25.0}
        result = split.compute_shares(
            100.0, ["alice", "bob"], exact_amounts=exact_amounts
        )
        expected = {"alice": 75.0, "bob": 25.0}
        assert result == expected

    def test_exact_split_missing_participants(self):
        """Test exact split with missing participant amounts."""
        exact_amounts = {"alice": 100.0}  # Missing bob
        split = ExactSplit(exact_amounts)
        with pytest.raises(
            ValueError, match="Exact amounts must be provided for all participants"
        ):
            split.compute_shares(100.0, ["alice", "bob"])

    def test_exact_split_incorrect_total(self):
        """Test exact split with amounts not summing to total."""
        exact_amounts = {"alice": 60.0, "bob": 30.0}  # Sum is 90, not 100
        split = ExactSplit(exact_amounts)
        with pytest.raises(
            ValueError, match="Exact amounts must sum to the total amount"
        ):
            split.compute_shares(100.0, ["alice", "bob"])

    def test_exact_split_key_cleaning(self):
        """Test exact split with key cleaning (capitalized keys)."""
        exact_amounts = {"Alice": 70.0, "Bob": 30.0}  # Capitalized keys
        split = ExactSplit(exact_amounts)
        result = split.compute_shares(100.0, ["alice", "bob"])  # lowercase participants
        expected = {"alice": 70.0, "bob": 30.0}
        assert result == expected

    def test_exact_split_rounding(self):
        """Test exact split preserves precise amounts."""
        exact_amounts = {"alice": 33.333, "bob": 33.333, "charlie": 33.334}
        split = ExactSplit(exact_amounts)
        result = split.compute_shares(100.0, ["alice", "bob", "charlie"])
        expected = {
            "alice": 33.333,
            "bob": 33.333,
            "charlie": 33.334,
        }  # Preserves exact precision until settlement
        assert result == expected

    def test_exact_split_str_representation(self):
        """Test string representation of ExactSplit."""
        split = ExactSplit()
        assert str(split) == "Exact split"


if __name__ == "__main__":
    pytest.main([__file__])
