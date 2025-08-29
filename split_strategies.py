class Split: ...


class EqualSplit:
    def compute_shares(self, amount, participants):
        mapping = {}
        for participant in participants:
            mapping[participant] = amount / len(participants)
        return mapping

    def __str__(self):
        return "Equal split"


class WeightsSplit(Split): ...


class PercentSplit(Split): ...


class ExactSplit(Split): ...
