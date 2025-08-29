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
    ledger.add_expense("Lino", 10.00, ["Nicola", "Bella"], "equal")
    ledger.add_expense(
        "Lino",
        100.00,
        ["Lino", "Victoria", "Bella"],
        "percent",
        percentages={"Lino": 50, "Victoria": 30, "Bella": 20},
    )
    ledger.add_expense(
        "Lino",
        50.00,
        ["Lino", "Victoria", "Bella"],
        "weights",
        weights={"Lino": 10, "Victoria": 5, "Bella": 1},
    )
    ledger.add_expense(
        "Lino",
        75.00,
        ["Lino", "Victoria", "Bella"],
        "exact",
        exact_amounts={"Lino": 20, "Victoria": 25, "Bella": 30},
    )
    ledger.list_expenses()
    ledger.list_balances()
    ledger.balances()
    ledger.list_balances()
    ledger.settle()
    ledger.list_balances()


if __name__ == "__main__":
    main()
