"""
Split strategies for the Expense Splitting Calculator application.

This module implements different algorithms for splitting expenses among
participants using the Strategy pattern.
"""

from constants import (
    MIN_PERCENTAGE,
    MAX_PERCENTAGE,
    PERCENTAGE_TOLERANCE,
    ROUNDING_PRECISION,
)


class Split:
    """
    Abstract base class for expense split strategies.

    All split strategies must implement the compute_shares method
    to define how expenses are divided among participants.
    """

    def compute_shares(
        self, amount: float, participants: list[str], *args, **kwargs
    ) -> dict:
        """
        Compute the share for each participant.

        Args:
            amount: Total amount to split
            participants: List of participant names
            *args, **kwargs: Strategy-specific arguments

        Returns:
            Dictionary mapping participant name to their share amount

        Raises:
            NotImplementedError: Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement compute_shares")


class EqualSplit(Split):
    """
    Split strategy that divides the amount equally among all participants.

    The simplest splitting method where each participant pays the same amount.
    """

    def compute_shares(self, amount: float, participants: list[str]) -> dict:
        """
        Compute equal shares for each participant.

        Args:
            amount: Total amount to split
            participants: List of participant names

        Returns:
            Dictionary with equal shares for each participant
        """
        share_per_person = amount / len(participants)
        return {participant: share_per_person for participant in participants}

    def __str__(self) -> str:
        return "Equal split"


class WeightsSplit(Split):
    """
    Split strategy that divides the amount proportionally based on weights.

    Participants with higher weights pay a larger share of the expense.
    """

    def __init__(self, weights=None):
        """
        Initialize with optional weights dictionary.

        Args:
            weights: Dictionary mapping participant names to their weights
        """
        self.weights = weights or {}

    def compute_shares(
        self, amount: float, participants: list[str], weights=None
    ) -> dict:
        """
        Compute proportional shares based on weights.

        Args:
            amount: Total amount to split
            participants: List of participant names
            weights: Optional weights dictionary (overrides instance weights)

        Returns:
            Dictionary with weighted shares for each participant

        Raises:
            ValueError: If weights are invalid or missing
            TypeError: If weight values are not numeric
        """
        weights = weights if weights is not None else self.weights

        if not weights:
            raise ValueError("Weights dictionary cannot be empty")

        # Clean and normalize weight keys
        weights_clean = {name.strip().lower(): weights[name] for name in weights.keys()}

        # Validate weight values
        for participant, weight in weights_clean.items():
            if not isinstance(weight, (int, float)):
                raise TypeError(f"Weight for {participant} must be a number")
            if weight < 0:
                raise ValueError(f"Weight for {participant} cannot be negative")

        # Check that all participants have weights
        if set(weights_clean.keys()) != set(participants):
            missing = set(participants) - set(weights_clean.keys())
            extra = set(weights_clean.keys()) - set(participants)
            error_msg = "Weights must be provided for all participants."
            if missing:
                error_msg += f" Missing weights for: {', '.join(missing)}"
            if extra:
                error_msg += f" Extra weights for: {', '.join(extra)}"
            raise ValueError(error_msg)

        # Calculate total weight and validate it's positive
        total_weight = sum(weights_clean[p] for p in participants)
        if total_weight == 0:
            raise ValueError(
                "Total weight must be greater than zero. All weights cannot be zero."
            )

        # Compute proportional shares
        return {
            participant: amount * weights_clean[participant] / total_weight
            for participant in participants
        }

    def __str__(self) -> str:
        return "Weights split"


class PercentSplit(Split):
    """
    Split strategy that divides the amount according to percentages.

    Percentages must sum to 100%. Each participant pays their specified
    percentage of the total expense.
    """

    def __init__(self, percentages=None):
        """
        Initialize with optional percentages dictionary.

        Args:
            percentages: Dictionary mapping participant names to percentages (0-100)
        """
        self.percentages = percentages or {}

    def compute_shares(
        self, amount: float, participants: list[str], percentages=None
    ) -> dict:
        """
        Compute shares based on percentages that must sum to 100%.

        Args:
            amount: Total amount to split
            participants: List of participant names
            percentages: Optional percentages dictionary (overrides instance percentages)

        Returns:
            Dictionary with percentage-based shares for each participant

        Raises:
            ValueError: If percentages are invalid, missing, or don't sum to 100%
            TypeError: If percentage values are not numeric
        """
        percentages = percentages if percentages is not None else self.percentages

        if not percentages:
            raise ValueError("Percentages dictionary cannot be empty")

        # Clean and normalize percentage keys
        percentages_clean = {
            name.strip().lower(): percentages[name] for name in percentages.keys()
        }

        # Validate percentage values
        for participant, percentage in percentages_clean.items():
            if not isinstance(percentage, (int, float)):
                raise TypeError(f"Percentage for {participant} must be a number")
            if percentage < MIN_PERCENTAGE:
                raise ValueError(
                    f"Percentage for {participant} must be at least {MIN_PERCENTAGE}%"
                )
            if percentage > MAX_PERCENTAGE:
                raise ValueError(
                    f"Percentage for {participant} cannot exceed {MAX_PERCENTAGE}%"
                )

        # Check that all participants have percentages
        if set(percentages_clean) != set(participants):
            raise ValueError("Percentages must be provided for all participants.")

        # Validate percentages sum to 100%
        total_percent = sum(percentages_clean[p] for p in participants)
        if abs(total_percent - 100.0) > PERCENTAGE_TOLERANCE:
            raise ValueError(
                f"Percentages must sum to 100% (currently {total_percent:.2f}%)"
            )

        # Compute percentage-based shares
        return {
            participant: amount * percentages_clean[participant] / 100
            for participant in participants
        }

    def __str__(self) -> str:
        return "Percent split"


class ExactSplit(Split):
    """
    Split strategy that uses exact amounts for each participant.

    The specified amounts must sum exactly to the total expense amount.
    This provides precise control over how much each participant pays.
    """

    def __init__(self, exact_amounts=None):
        """
        Initialize with optional exact amounts dictionary.

        Args:
            exact_amounts: Dictionary mapping participant names to exact amounts
        """
        self.exact_amounts = exact_amounts or {}

    def compute_shares(
        self, amount: float, participants: list[str], exact_amounts=None
    ) -> dict:
        """
        Compute shares using exact amounts that must sum to the total.

        Args:
            amount: Total amount to split
            participants: List of participant names
            exact_amounts: Optional exact amounts dictionary (overrides instance amounts)

        Returns:
            Dictionary with exact shares for each participant

        Raises:
            ValueError: If amounts are missing or don't sum to the total
        """
        exact_amounts = (
            exact_amounts if exact_amounts is not None else self.exact_amounts
        )

        if not exact_amounts:
            raise ValueError("Exact amounts must be provided for all participants.")

        # Clean and normalize amount keys
        exact_amounts_clean = {
            name.strip().lower(): exact_amounts[name] for name in exact_amounts.keys()
        }

        # Check that all participants have exact amounts
        if set(exact_amounts_clean.keys()) != set(participants):
            raise ValueError("Exact amounts must be provided for all participants.")

        # Validate that amounts sum to the total (with rounding tolerance)
        total = sum(exact_amounts_clean[p] for p in participants)
        if round(total, ROUNDING_PRECISION) != round(amount, ROUNDING_PRECISION):
            raise ValueError("Exact amounts must sum to the total amount.")

        return {
            participant: exact_amounts_clean[participant]
            for participant in participants
        }

    def __str__(self) -> str:
        return "Exact split"
