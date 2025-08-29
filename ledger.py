from models import Person, Expense
from split_strategies import Split, EqualSplit, WeightsSplit, PercentSplit, ExactSplit


class Ledger:
    def __init__(self, people={}, expenses=[]):
        self.people = people
        self.expenses = expenses

    def add_person(self, name, balance=0, paid=0, owe=0):
        name_clean = name.strip().lower()
        if name_clean not in self.people.keys():
            person = Person(name_clean, balance, paid, owe)
            self.people[name_clean] = person
        else:
            print(f"Person {name} already exists!")

    # TODO automatically create person (payer and participants) if not yet in people dictionary
    def add_expense(self, payer, amount, participants, split):
        payer_clean = payer.strip().lower()
        participants_clean = [
            participant.strip().lower() for participant in participants
        ]

        if payer_clean not in self.people.keys():
            raise IndexError(
                f"Person {payer} does not yet exist. Create {payer} with .add_person() first before adding as a payer."
            )
        for participant in participants_clean:
            if participant not in self.people.keys():
                raise IndexError(
                    f"Person {participant} does not yet exist. Create {participant} with .add_person() first before adding as a participant."
                )

        expense = Expense(payer_clean, amount, participants_clean, split)
        self.expenses.append(expense)

    def balances(self):
        for expense in self.expenses:
            self.people[expense.payer].paid = expense.amount
            mapping = expense.split.compute_shares(expense.amount, expense.participants)
            for participant in mapping:
                self.people[participant].owe += mapping[participant]
        for person in self.people.values():
            person.balance = person.paid - person.owe

    def list_expenses(self):
        expenses_str = "\n".join(str(expense) for expense in self.expenses)
        print(f"Expenses:\n{expenses_str}")

    def list_balances(self):
        sorted_people = sorted(
            self.people.values(), key=lambda person: person.balance, reverse=True
        )
        people_str = "\n".join(str(person) for person in sorted_people)
        print(f"People:\n{people_str}")

    def __str__(self):
        people_str = "\n".join(str(person) for person in self.people.values())
        expenses_str = "\n".join(str(expense) for expense in self.expenses)
        return f"People:\n{people_str}\n\nExpenses:\n{expenses_str}"
