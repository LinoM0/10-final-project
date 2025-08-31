# Constants for validation
MIN_WEIGHT = 0.01
MAX_WEIGHT = 1000000
MIN_PERCENTAGE = 0.01
MAX_PERCENTAGE = 100.0
PERCENTAGE_TOLERANCE = 0.01


class Split:
    """
    Abstract base class for split strategies.
    """

    def compute_shares(
        self, amount: float, participants: list[str], *args, **kwargs
    ) -> dict:
        """
        Compute the shares for each participant.
        
        :param amount: Total amount to split
        :param participants: List of participant names
        :return: Dictionary mapping participant to their share
        :raises NotImplementedError: This method must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement compute_shares")


class EqualSplit(Split):
    """
    Split strategy: split amount equally among participants.
    """

    def compute_shares(self, amount: float, participants: list[str]) -> dict:
        """
        Compute equal shares for each participant without rounding.
        """
        mapping = {
            participant: amount / len(participants) for participant in participants
        }
        return mapping

    def __str__(self) -> str:
        return "Equal split"


class WeightsSplit(Split):
    """
    Split strategy: split amount proportionally to weights.
    """

    def __init__(self, weights=None):
        """
        :param weights: Dictionary mapping participant to their weight
        """
        self.weights = weights or {}

    def compute_shares(
        self, amount: float, participants: list[str], weights=None
    ) -> dict:
        """
        Compute shares for each participant based on weights.
        
        :param amount: Total amount to split
        :param participants: List of participant names
        :param weights: Optional weights dictionary
        :return: Dictionary mapping participant to their share
        :raises ValueError: If weights are missing or invalid
        """
        weights = weights if weights is not None else self.weights
        
        if not weights:
            raise ValueError("Weights dictionary cannot be empty")
        
        weights_clean = {w.strip().lower(): weights[w] for w in weights.keys()}
        
        # Validate weights values
        for participant, weight in weights_clean.items():
            if not isinstance(weight, (int, float)):
                raise TypeError(f"Weight for {participant} must be a number")
            if weight < 0:  # Allow zero weights for backward compatibility
                raise ValueError(f"Weight for {participant} cannot be negative")
        
        if set(weights_clean.keys()) != set(participants):
            missing = set(participants) - set(weights_clean.keys())
            extra = set(weights_clean.keys()) - set(participants)
            error_msg = "Weights must be provided for all participants."
            if missing:
                error_msg += f" Missing weights for: {', '.join(missing)}"
            if extra:
                error_msg += f" Extra weights for: {', '.join(extra)}"
            raise ValueError(error_msg)
            
        total_weight = sum(weights_clean[p] for p in participants)
        if total_weight == 0:
            raise ValueError("Total weight must be greater than zero. All weights cannot be zero.")
            
        mapping = {
            participant: amount * weights_clean[participant] / total_weight
            for participant in participants
        }
        return mapping

    def __str__(self) -> str:
        return "Weights split"


class PercentSplit(Split):
    """
    Split strategy: split amount according to percentages (must sum to 100%).
    """

    def __init__(self, percentages=None):
        """
        :param percentages: Dictionary mapping participant to their percentage (0-100)
        """
        self.percentages = percentages or {}

    def compute_shares(
        self, amount: float, participants: list[str], percentages=None
    ) -> dict:
        """
        Compute shares for each participant based on percentages.
        """
        percentages = percentages if percentages is not None else self.percentages
        
        if not percentages:
            raise ValueError("Percentages dictionary cannot be empty")
            
        percentages_clean = {
            p.strip().lower(): percentages[p] for p in percentages.keys()
        }
        
        # Validate percentage values
        for participant, percentage in percentages_clean.items():
            if not isinstance(percentage, (int, float)):
                raise TypeError(f"Percentage for {participant} must be a number")
            if percentage < MIN_PERCENTAGE:
                raise ValueError(f"Percentage for {participant} must be at least {MIN_PERCENTAGE}%")
            if percentage > MAX_PERCENTAGE:
                raise ValueError(f"Percentage for {participant} cannot exceed {MAX_PERCENTAGE}%")
        
        if set(percentages_clean) != set(participants):
            raise ValueError("Percentages must be provided for all participants.")
            
        total_percent = sum(percentages_clean[p] for p in participants)
        if abs(total_percent - 100.0) > PERCENTAGE_TOLERANCE:
            raise ValueError(f"Percentages must sum to 100% (currently {total_percent:.2f}%)")
            
        mapping = {
            participant: amount * percentages_clean[participant] / 100
            for participant in participants
        }
        return mapping

    def __str__(self) -> str:
        return "Percent split"


class ExactSplit(Split):
    """
    Split strategy: split amount according to exact values (must sum to total amount).
    """

    def __init__(self, exact_amounts=None):
        """
        :param exact_amounts: Dictionary mapping participant to their exact share
        """
        self.exact_amounts = exact_amounts or {}

    def compute_shares(
        self, amount: float, participants: list[str], exact_amounts=None
    ) -> dict:
        """
        Compute shares for each participant based on exact amounts.
        """
        exact_amounts = (
            exact_amounts if exact_amounts is not None else self.exact_amounts
        )
        exact_amounts_clean = {
            e.strip().lower(): exact_amounts[e] for e in exact_amounts.keys()
        }
        if not exact_amounts_clean or set(exact_amounts_clean.keys()) != set(
            participants
        ):
            raise ValueError("Exact amounts must be provided for all participants.")
        total = sum(exact_amounts_clean[p] for p in participants)
        if round(total, 2) != round(amount, 2):
            raise ValueError("Exact amounts must sum to the total amount.")
        mapping = {
            participant: exact_amounts_clean[participant]
            for participant in participants
        }
        return mapping

    def __str__(self) -> str:
        return "Exact split"
