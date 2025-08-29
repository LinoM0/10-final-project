class Ledger:
    def __init__(self, people={}, expenses=[]):
        self.people = people
        self.expenses = expenses

    def add_person(self, name):
        person = Person(name)
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
        return (
            f"People:\n"
            f"{self.people['Lino']}\n"
            f"{self.people['Victoria']}\n\n"
            f"Expenses:\n"
            f"{self.expenses[0]}"
        )


class Person:
    def __init__(self, name, balance=0):
        self.name = name
        self.balance = balance

    def __str__(self):
        return f"{self.name} with balance: {self.balance}£"


class Expense:
    def __init__(self, payer, amount):
        self.payer = payer
        self.amount = amount

    def __str__(self):
        return f"{self.amount}£ from {self.payer}"


def main():
    ledger = Ledger()
    ledger.add_person("Lino")
    ledger.add_person("Victoria")
    ledger.add_expense("Lino", 10)
    print(ledger)
    ledger.split()
    print(ledger)


# def function_1(): ...


# def function_2(): ...


# def function_n(): ...


if __name__ == "__main__":
    main()
