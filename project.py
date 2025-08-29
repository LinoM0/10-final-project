class Ledger:
    def __init__(self, people={}, expenses=[]):
        self.people = people
        self.expenses = expenses

    def add_person(self, name, balance=0):
        name_clean = name.strip().lower()
        if name_clean not in self.people.keys():
            person = Person(name_clean, balance)
            self.people[name_clean] = person
        else:
            print(f"Person {name} already exists!")

    def add_expense(self, payer, amount):
        payer_clean = payer.strip().lower()
        if payer_clean in self.people.keys():
            expense = Expense(payer_clean, amount)
            self.people[f"{payer_clean}"].balance += amount
            self.expenses.append(expense)
        else:
            raise IndexError(
                f"Person {payer} does not yet exist. Create {payer} with .add_person() first before adding as a payer."
            )

    def split(self):
        total = 0
        for expense in self.expenses:
            total += expense.amount
        share = total / len(self.people.keys())
        for person in self.people.values():
            person.balance = round(person.balance - share, 2)

    def __str__(self):
        people_str = "\n".join(str(person) for person in self.people.values())
        expenses_str = "\n".join(str(expense) for expense in self.expenses)
        return f"People:\n{people_str}\n\nExpenses:\n{expenses_str}"


def is_valid_money(value):
    if not isinstance(value, (int, float)):
        return False
    value_str = f"{value:.10f}".rstrip("0").rstrip(".")
    if "." in value_str:
        decimals = value_str.split(".")[1]
        return len(decimals) <= 2
    return True


class Person:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

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
        if not isinstance(balance, (int, float)):
            raise ValueError("Balance is not numeric")
        if not is_valid_money(balance):
            raise ValueError("Balance must have at most two decimal places")
        self._balance = balance

    def __str__(self):
        return f"{self.name.capitalize()} with balance: {self.balance}£"


class Expense:
    def __init__(self, payer, amount):
        self.payer = payer
        self.amount = amount

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
        if not isinstance(amount, (int, float)):
            raise ValueError("Expense is not numeric. Input in format x.yz£")
        if not is_valid_money(amount):
            raise ValueError("Expense must have at most two decimal places")
        self._amount = amount

    def __str__(self):
        return f"{self.amount}£ from {self.payer.capitalize()}"


def main():
    ledger = Ledger()
    ledger.add_person("LiNo")
    ledger.add_person("Lino")
    ledger.add_person("victoria")
    ledger.add_person("Bella")
    ledger.add_expense("Lino", 10.00)
    ledger.add_expense("Victoria", 20.1)
    ledger.add_expense("Lino", 5.35)
    # ledger.add_expense("Rolli", 5)
    print(ledger)
    ledger.split()
    print(ledger)


if __name__ == "__main__":
    main()
