class Ledger:
    def __init__(self, people=[], expenses=[]):
        self.people = people
        self.expenses = expenses

    def add_person(self, name):
        person = Person(name)
        self.people.append(person)

    def add_expense(self, payer, amount):
        expense = Expense(payer, amount)
        self.expenses.append(expense)

    def __str__(self):
        return f"{self.people} and {self.expenses}"


class Person:
    def __init__(self, name):
        self.name = name


class Expense:
    def __init__(self, payer, amount):
        self.payer = payer
        self.amount = amount


def main():
    ledger = Ledger()
    ledger.add_person("Lino")
    ledger.add_person("Victoria")
    ledger.add_expense("Lino", 10)
    print(ledger)


# def function_1(): ...


# def function_2(): ...


# def function_n(): ...


if __name__ == "__main__":
    main()
