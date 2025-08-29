from ledger import Ledger


def main():
    ledger = Ledger()
    ledger.add_person("Lino")
    ledger.add_person("Victoria")
    ledger.add_person("Bella")
    ledger.add_person("Rogek")
    ledger.add_expense("Lino", 15.00, ["Lino", "Victoria"], "equal")
    ledger.add_expense("Lino", 25.00, ["Lino", "Bella"], "equal")
    ledger.add_expense("Rogek", 45.00, ["Lino", "Victoria", "Bella"], "equal")
    ledger.list_expenses()
    ledger.list_balances()
    ledger.balances()
    ledger.list_balances()
    ledger.settle()


if __name__ == "__main__":
    main()
