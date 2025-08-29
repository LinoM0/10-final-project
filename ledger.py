from models import Person, Expense


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

        self.people[expense.payer].paid += expense.amount

    def balances(self):
        for expense in self.expenses:
            mapping = expense.split.compute_shares(expense.amount, expense.participants)
            for participant in mapping:
                self.people[participant].owe += mapping[participant]
        for person in self.people.values():
            person.balance = person.paid - person.owe

    def settle(self):
        creditors = {}
        debitors = {}
        for person in self.people.values():
            if person.balance > 0:
                creditors[person.name] = person
            elif person.balance < 0:
                debitors[person.name] = person
            else:
                pass
        while max(person.balance for person in creditors.values()) > 0:
            max_creditor = max(creditors.values(), key=lambda person: person.balance)
            max_debitor = min(debitors.values(), key=lambda person: person.balance)
            transfer_amount = min(max_creditor.balance, abs(max_debitor.balance))
            print(
                f"{max_debitor.name.capitalize()} → {max_creditor.name.capitalize()}: {transfer_amount}£"
            )
            creditors[max_creditor.name].balance -= transfer_amount
            debitors[max_debitor.name].balance += transfer_amount

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
