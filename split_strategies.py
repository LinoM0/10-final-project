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
        """
        raise NotImplementedError("Subclasses must implement compute_shares")


class EqualSplit(Split):
    """
    Split strategy: split amount equally among participants.
    """

    def compute_shares(self, amount: float, participants: list[str]) -> dict:
        """
        Compute equal shares for each participant.
        """
        mapping = {
            participant: round(amount / len(participants), 2)
            for participant in participants
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
        """
        weights = weights if weights is not None else self.weights
        weights_clean = {w.strip().lower(): weights[w] for w in weights.keys()}
        if not weights_clean or set(weights_clean.keys()) != set(participants):
            raise ValueError("Weights must be provided for all participants.")
        total_weight = sum(weights_clean[p] for p in participants)
        if total_weight == 0:
            raise ValueError("Total weight must be greater than zero.")
        mapping = {
            participant: round(amount * weights_clean[participant] / total_weight, 2)
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
        percentages_clean = {
            p.strip().lower(): percentages[p] for p in percentages.keys()
        }
        if not percentages or set(percentages_clean) != set(participants):
            raise ValueError("Percentages must be provided for all participants.")
        total_percent = sum(percentages_clean[p] for p in participants)
        if round(total_percent, 2) != 100.0:
            raise ValueError("Percentages must sum to 100%.")
        mapping = {
            participant: round(amount * percentages_clean[participant] / 100, 2)
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
            participant: round(exact_amounts_clean[participant], 2)
            for participant in participants
        }
        return mapping

    def __str__(self) -> str:
        return "Exact split"
