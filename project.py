class Ledger:
    def __init__(self, people={}, expenses=[]):
        self.people = people
        self.expenses = expenses

    def add_person(self, name, balance=0):
        person = Person(name, balance)
        self.people[name] = person

    def add_expense(self, payer, amount):
        expense = Expense(payer, amount)
        self.people[f"{payer}"].balance += amount
        self.expenses.append(expense)

    def split(self):
        total = 0
        for expense in self.expenses:
            total += expense.amount
        for person in self.people.values():
            person.balance -= total / len(self.people.keys())

    def __str__(self):
        people_str = "\n".join(str(person) for person in self.people.values())
        expenses_str = "\n".join(str(expense) for expense in self.expenses)
        return f"People:\n{people_str}\n\nExpenses:\n{expenses_str}"


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
        self._balance = balance

    def __str__(self):
        return f"{self.name} with balance: {self.balance}£"


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
            raise ValueError("Expense is not numeric")
        self._amount = amount

    def __str__(self):
        return f"{self.amount}£ from {self.payer}"


def main():
    ledger = Ledger()
    ledger.add_person("Lino")
    ledger.add_person("Victoria")
    ledger.add_person("Bella", -100)
    ledger.add_expense("Lino", 10)
    ledger.add_expense("Victoria", 20)
    ledger.add_expense("Lino", 5)
    print(ledger)
    ledger.split()
    print(ledger)


# def function_1(): ...


# def function_2(): ...


# def function_n(): ...


if __name__ == "__main__":
    main()
