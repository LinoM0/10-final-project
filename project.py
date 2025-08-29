from ledger import Ledger


def main():
    ledger = Ledger()
    ledger.add_person("Lino")
    ledger.add_person("Victoria")
    ledger.add_person("Bella")
    ledger.add_expense("Lino", 15.00, ["Lino", "Victoria"], "equal")
    ledger.list_expenses()
    ledger.list_balances()
    ledger.balances()
    ledger.list_balances()


if __name__ == "__main__":
    main()
