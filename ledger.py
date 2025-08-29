from models import Person, Expense


class Ledger:
    """
    Ledger class to manage people and expenses, and perform balance calculations and settlements.
    """

    def __init__(self, people=None, expenses=None):
        """
        Initialize a Ledger instance.
        :param people: Optional dictionary of people (name -> Person)
        :param expenses: Optional list of Expense objects
        """
        self.people: dict[str, Person] = people if people is not None else {}
        self.expenses: list[Expense] = expenses if expenses is not None else []

    def add_person(
        self, name: str, balance: float = 0, paid: float = 0, owe: float = 0
    ) -> None:
        """
        Add a person to the ledger if not already present.
        :param name: Name of the person
        :param balance: Initial balance
        :param paid: Initial paid amount
        :param owe: Initial owed amount
        """
        name_clean = name.strip().lower()
        if name_clean in self.people:
            print(f"Person {name} already exists!")
            return
        self.people[name_clean] = Person(name_clean, balance, paid, owe)

    def add_expense(
        self, payer: str, amount: float, participants: list[str], split: str, **kwargs
    ) -> None:
        """
        Add an expense to the ledger.
        :param payer: Name of the payer
        :param amount: Expense amount
        :param participants: List of participant names
        :param split: Split strategy ('equal', 'weights', 'percent', 'exact')
        :param kwargs: Additional arguments for split strategies
        """
        payer_clean = payer.strip().lower()
        participants_clean = [p.strip().lower() for p in participants]

        if payer_clean not in self.people:
            answer = input(
                f"Person {payer.capitalize()} does not exist. Create? (y/n) "
            )
            if answer.lower() == "y":
                self.add_person(payer)
            else:
                raise IndexError(
                    f"Person {payer.capitalize()} does not exist. Create them first."
                )
        for participant in participants_clean:
            if participant not in self.people:
                answer = input(
                    f"Person {participant.capitalize()} does not exist. Create? (y/n) "
                )
                if answer.lower() == "y":
                    self.add_person(participant)
                else:
                    raise IndexError(
                        f"Person {participant.capitalize()} does not exist. Create them first."
                    )

        expense = Expense(payer_clean, amount, participants_clean, split, **kwargs)
        self.expenses.append(expense)
        self.people[expense.payer].paid += expense.amount

    def balances(self) -> None:
        """
        Calculate and update each person's balance based on paid and owed amounts.
        """
        # Reset owe for all people
        for person in self.people.values():
            person.owe = 0
        for expense in self.expenses:
            mapping = expense.split.compute_shares(expense.amount, expense.participants)
            for participant, share in mapping.items():
                self.people[participant].owe += share
        for person in self.people.values():
            person.balance = round(person.paid - person.owe, 2)

    def settle(self) -> None:
        """
        Settle debts between people by printing the minimal set of transactions.
        """
        creditors = {p.name: p for p in self.people.values() if p.balance > 0}
        debitors = {p.name: p for p in self.people.values() if p.balance < 0}
        while creditors and debitors and max(p.balance for p in creditors.values()) > 0:
            max_creditor = max(creditors.values(), key=lambda p: p.balance)
            max_debitor = min(debitors.values(), key=lambda p: p.balance)
            transfer_amount = round(
                min(max_creditor.balance, abs(max_debitor.balance)), 2
            )
            print(
                f"{max_debitor.name.capitalize()} → {max_creditor.name.capitalize()}: {transfer_amount}£"
            )
            max_creditor.balance = round(max_creditor.balance - transfer_amount, 2)
            max_debitor.balance = round(max_debitor.balance + transfer_amount, 2)
            if round(max_creditor.balance, 2) == 0:
                del creditors[max_creditor.name]
            if round(max_debitor.balance, 2) == 0:
                del debitors[max_debitor.name]

    def list_expenses(self) -> None:
        """
        Print all expenses in the ledger.
        """
        if not self.expenses:
            print("No expenses recorded.")
            return
        expenses_str = "\n".join(str(expense) for expense in self.expenses)
        print(f"Expenses:\n{expenses_str}")

    def list_balances(self) -> None:
        """
        Print all people and their balances, sorted by balance descending.
        """
        if not self.people:
            print("No people in ledger.")
            return
        sorted_people = sorted(
            self.people.values(), key=lambda p: p.balance, reverse=True
        )
        people_str = "\n".join(str(person) for person in sorted_people)
        print(f"People:\n{people_str}")

    def __str__(self) -> str:
        """
        Return a string representation of the ledger, listing people and expenses.
        """
        people_str = "\n".join(str(person) for person in self.people.values())
        expenses_str = "\n".join(str(expense) for expense in self.expenses)
        return f"People:\n{people_str}\n\nExpenses:\n{expenses_str}"
