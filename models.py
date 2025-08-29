from split_strategies import EqualSplit, WeightsSplit, PercentSplit, ExactSplit
import inflect

p = inflect.engine()


# TODO Properties for paid and owe
class Person:
    def __init__(self, name, balance, paid, owe):
        self.name = name
        self.balance = balance
        self.paid = paid
        self.owe = owe

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not name:
            raise ValueError("Missing name")
        self._name = name

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, balance):
        if not is_valid_money(balance):
            raise ValueError("Balance not valid monetary amount (enter as x.yz£)")
        self._balance = balance

    def __str__(self):
        return f"{self.name.capitalize()} with balance: {self.balance}£"


class Expense:
    def __init__(self, payer, amount, participants, split):
        self.payer = payer
        self.amount = amount
        self.participants = participants
        if split == "equal":
            self.split = EqualSplit()
        elif split == "weights":
            self.split = WeightsSplit()
        elif split == "percent":
            self.split = PercentSplit()
        elif split == "exact":
            self.split = ExactSplit()
        else:
            raise ValueError("Split method not valid")

    @property
    def payer(self):
        return self._payer

    @payer.setter
    def payer(self, payer):
        if not payer:
            raise ValueError("Missing payer")
        self._payer = payer

    @property
    def amount(self):
        return self._amount

    @amount.setter
    def amount(self, amount):
        if not is_valid_money(amount):
            raise ValueError("Expense not valid monetary amount (enter as x.yz£)")
        if amount < 0:
            raise ValueError("Expense must be positive.")
        self._amount = amount

    @property
    def participants(self):
        return self._participants

    @participants.setter
    def participants(self, participants):
        if not participants:
            raise ValueError("Missing participants")
        self._participants = participants

    @property
    def split(self):
        return self._split

    @split.setter
    def split(self, split):
        if not isinstance(split, (EqualSplit, WeightsSplit, PercentSplit, ExactSplit)):
            raise ValueError("Split method not valid")
        self._split = split

    def __str__(self):
        participants_str = p.join([name.capitalize() for name in self.participants])
        return f"{self.amount}£ paid by {self.payer.capitalize()} due for {participants_str} with {self.split} method"


def is_valid_money(value):
    if not isinstance(value, (int, float)):
        return False
    value_str = f"{value:.10f}".rstrip("0").rstrip(".")
    if "." in value_str:
        decimals = value_str.split(".")[1]
        return len(decimals) <= 2
    return True
