#!/usr/bin/env python3
"""
Interactive Expense Splitting Application

This application provides a command-line interface for managing shared expenses
among groups of people with multiple splitting strategies and debt settlement.
"""

from ledger import Ledger
from utils import format_currency, clean_input, validate_name, parse_amount_input
from constants import MENU_OPTIONS, SPLIT_TYPES, DEFAULT_CURRENCY_SYMBOL


# =============================================================================
# USER INTERFACE FUNCTIONS
# =============================================================================


def print_banner():
    """Display the application welcome banner."""
    print("=" * 60)
    print("           💰 EXPENSE SPLITTING CALCULATOR 💰")
    print("=" * 60)
    print("Welcome! This app helps you split expenses fairly among friends.")
    print()


def print_menu():
    """Display the main menu options."""
    print("\n" + "─" * 40)
    print("📋 MENU OPTIONS:")
    print("─" * 40)
    print("1. ➕ Add a person")
    print("2. 🏷️  Add an expense")
    print("3. 👥 View all people")
    print("4. 🧾 View all expenses")
    print("5. 💳 View current balances")
    print("6. 📊 Show summary")
    print("7. ⚖️  Settle debts")
    print("8. ❌ Exit")
    print("─" * 40)


def get_user_choice():
    """Get and validate main menu choice from user."""
    while True:
        try:
            choice = input("\nEnter your choice (1-8): ").strip()
            if choice in MENU_OPTIONS:
                return int(choice)
            else:
                print("❌ Invalid choice. Please enter a number between 1 and 8.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            exit(0)
        except ValueError:
            print("❌ Please enter a valid number.")


# =============================================================================
# INPUT VALIDATION FUNCTIONS
# =============================================================================


def get_monetary_input(prompt, min_amount=0.01, max_amount=999999.99):
    """
    Get and validate monetary input from user.

    Args:
        prompt: Input prompt message
        min_amount: Minimum allowed amount
        max_amount: Maximum allowed amount

    Returns:
        Validated monetary amount as float
    """
    while True:
        try:
            value = input(prompt).strip()
            is_valid, amount, error_msg = parse_amount_input(value)

            if not is_valid:
                print(f"❌ {error_msg}")
                continue

            if amount < min_amount:
                print(f"❌ Amount must be at least {format_currency(min_amount)}")
                continue

            if amount > max_amount:
                print(f"❌ Amount cannot exceed {format_currency(max_amount)}")
                continue

            return amount

        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            exit(0)


def get_name_input(prompt, existing_names=None):
    """
    Get and validate name input from user.

    Args:
        prompt: Input prompt message
        existing_names: List of existing names to check for duplicates

    Returns:
        Validated name string
    """
    while True:
        try:
            name = input(prompt).strip()
            is_valid, error_msg = validate_name(name)

            if not is_valid:
                print(f"❌ {error_msg}")
                continue

            # Check for duplicates
            if existing_names and clean_input(name) in [
                clean_input(n) for n in existing_names
            ]:
                print(f"❌ Name '{name}' already exists.")
                continue

            return name

        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            exit(0)


def get_split_type():
    """Get split type selection from user."""
    print("\nChoose split method:")
    print("  1. Equal split")
    print("  2. Weighted split")
    print("  3. Percentage split")
    print("  4. Exact amount split")

    while True:
        try:
            choice = input("Enter choice (1-4): ").strip()
            if choice in SPLIT_TYPES:
                return SPLIT_TYPES[choice]
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            exit(0)


# =============================================================================
# PARTICIPANT SELECTION FUNCTIONS
# =============================================================================


def get_participants_interactive(ledger):
    """
    Get expense participants interactively from available people.

    Args:
        ledger: The Ledger instance

    Returns:
        List of selected participant names, or None if no people available
    """
    if not ledger.people:
        print("❌ No people available. Please add people first.")
        return None

    print("\nAvailable people:")
    people_list = list(ledger.people.keys())
    for i, person in enumerate(people_list, 1):
        print(f"  {i}. {person.capitalize()}")

    print(
        "\nSelect participants (enter numbers separated by commas, or 'all' for everyone):"
    )

    while True:
        try:
            selection = input("Participants: ").strip()

            if selection.lower() == "all":
                return people_list.copy()

            # Parse comma-separated numbers
            indices = [int(x.strip()) for x in selection.split(",")]

            # Validate indices
            if all(1 <= i <= len(people_list) for i in indices):
                return [people_list[i - 1] for i in indices]
            else:
                print(f"❌ Please enter numbers between 1 and {len(people_list)}.")

        except ValueError:
            print("❌ Please enter valid numbers separated by commas.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            exit(0)


# =============================================================================
# SPLIT DETAILS FUNCTIONS
# =============================================================================


def get_split_details(split_type, participants):
    """
    Get additional details for specific split types.

    Args:
        split_type: Type of split ('weights', 'percent', 'exact')
        participants: List of participant names

    Returns:
        Dictionary with split-specific parameters
    """
    if split_type == "weights":
        return get_weights_input(participants)
    elif split_type == "percent":
        return get_percentages_input(participants)
    elif split_type == "exact":
        return get_exact_amounts_input(participants)
    else:
        return {}


def get_weights_input(participants):
    """Get weights for each participant."""
    weights = {}
    print("\nEnter weights for each participant:")

    for participant in participants:
        while True:
            try:
                weight = float(input(f"Weight for {participant.capitalize()}: "))
                if weight < 0:
                    print("❌ Weight cannot be negative.")
                    continue
                weights[participant] = weight
                break
            except ValueError:
                print("❌ Please enter a valid number.")
            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 Goodbye!")
                exit(0)

    return {"weights": weights}


def get_percentages_input(participants):
    """Get percentages for each participant that must sum to 100%."""
    percentages = {}
    total = 0

    print("\nEnter percentages for each participant (must sum to 100%):")

    for i, participant in enumerate(participants):
        while True:
            try:
                if i == len(participants) - 1:
                    # Last participant gets the remaining percentage
                    remaining = 100 - total
                    print(
                        f"Remaining percentage for {participant.capitalize()}: {remaining}%"
                    )
                    percentages[participant] = remaining
                    break
                else:
                    percent = float(
                        input(f"Percentage for {participant.capitalize()} (%): ")
                    )
                    if percent < 0 or percent > 100:
                        print("❌ Percentage must be between 0 and 100.")
                        continue
                    if total + percent > 100:
                        print(f"❌ Total would exceed 100%. Remaining: {100 - total}%")
                        continue
                    percentages[participant] = percent
                    total += percent
                    break
            except ValueError:
                print("❌ Please enter a valid number.")
            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 Goodbye!")
                exit(0)

    return {"percentages": percentages}


def get_exact_amounts_input(participants):
    """Get exact amounts for each participant."""
    exact_amounts = {}

    print("\nEnter exact amounts for each participant:")

    for participant in participants:
        while True:
            try:
                amount = get_monetary_input(
                    f"Amount for {participant.capitalize()} ({DEFAULT_CURRENCY_SYMBOL}): "
                )
                exact_amounts[participant] = amount
                break
            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 Goodbye!")
                exit(0)

    return {"exact_amounts": exact_amounts}


# =============================================================================
# MAIN FUNCTIONALITY FUNCTIONS
# =============================================================================


def add_person_interactive(ledger):
    """Interactively add a person to the ledger."""
    print("\n➕ ADD A PERSON")
    print("─" * 20)

    while True:
        try:
            existing_names = list(ledger.people.keys())
            name = get_name_input(
                "Enter person's name (or 'back' to return): ", existing_names
            )

            if name.lower() == "back":
                return

            ledger.add_person(name)
            print(f"✅ {name.capitalize()} has been added!")
            return

        except (ValueError, TypeError) as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


def add_expense_interactive(ledger):
    """Interactively add an expense to the ledger."""
    print("\n🏷️  ADD AN EXPENSE")
    print("─" * 20)

    if not ledger.people:
        print("❌ No people available. Please add people first.")
        return

    try:
        # Get payer
        print("\nWho paid for this expense?")
        people_list = list(ledger.people.keys())
        for i, person in enumerate(people_list, 1):
            print(f"  {i}. {person.capitalize()}")

        while True:
            try:
                payer_choice = int(input("Enter number: "))
                if 1 <= payer_choice <= len(people_list):
                    payer = people_list[payer_choice - 1]
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(people_list)}.")
            except ValueError:
                print("❌ Please enter a valid number.")

        # Get amount
        amount = get_monetary_input(
            f"Enter expense amount ({DEFAULT_CURRENCY_SYMBOL}): "
        )

        # Get participants
        participants = get_participants_interactive(ledger)
        if not participants:
            return

        # Get split type and details
        split_type = get_split_type()
        kwargs = get_split_details(split_type, participants)

        # Add the expense
        ledger.add_expense(payer, amount, participants, split_type, **kwargs)
        print(f"✅ Expense of {format_currency(amount)} added successfully!")

    except (ValueError, TypeError, IndexError) as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def view_people(ledger):
    """Display all people in the ledger."""
    print("\n👥 ALL PEOPLE")
    print("─" * 20)

    if not ledger.people:
        print("No people added yet.")
    else:
        for i, (name, person) in enumerate(ledger.people.items(), 1):
            print(f"{i}. {name.capitalize()}")

    input("\nPress Enter to continue...")


def view_expenses(ledger):
    """Display all expenses in the ledger."""
    print("\n🧾 ALL EXPENSES")
    print("─" * 20)
    ledger.list_expenses()
    input("\nPress Enter to continue...")


def view_balances(ledger):
    """Display current balances."""
    print("\n💳 CURRENT BALANCES")
    print("─" * 20)
    ledger.balances()
    ledger.list_balances()
    input("\nPress Enter to continue...")


def show_summary(ledger):
    """Display comprehensive ledger summary."""
    print("\n📊 LEDGER SUMMARY")
    print("─" * 30)

    if not ledger.people:
        print("No people in the ledger yet.")
        input("\nPress Enter to continue...")
        return

    print(f"👥 People: {len(ledger.people)}")
    print(f"🧾 Expenses: {len(ledger.expenses)}")

    if ledger.expenses:
        total_expenses = sum(expense.amount for expense in ledger.expenses)
        print(f"💰 Total amount: {format_currency(total_expenses)}")
        print(
            f"📈 Average expense: {format_currency(total_expenses / len(ledger.expenses))}"
        )

        ledger.balances()  # Calculate current balances

        creditors = [p for p in ledger.people.values() if p.balance > 0]
        debtors = [p for p in ledger.people.values() if p.balance < 0]

        if creditors:
            max_creditor = max(creditors, key=lambda p: p.balance)
            print(
                f"🏆 Biggest creditor: {max_creditor.name.capitalize()} "
                f"({format_currency(max_creditor.balance)})"
            )

        if debtors:
            max_debtor = min(debtors, key=lambda p: p.balance)
            print(
                f"💸 Biggest debtor: {max_debtor.name.capitalize()} "
                f"({format_currency(abs(max_debtor.balance))})"
            )

    input("\nPress Enter to continue...")


def settle_debts(ledger):
    """Settle all debts and show final state."""
    print("\n⚖️  SETTLING DEBTS")
    print("─" * 20)

    if not ledger.expenses:
        print("No expenses to settle.")
        input("\nPress Enter to continue...")
        return

    print("Calculating balances...")
    ledger.balances()

    print("\nCurrent balances:")
    ledger.list_balances()

    print("\nSettlement transactions:")
    print("─" * 30)
    ledger.settle()

    print("\n✅ Settlement complete!")
    print("\nFinal balances:")
    ledger.list_balances()

    input("\nPress Enter to continue...")


def main():
    """Main application loop with menu-driven interface."""
    print_banner()
    ledger = Ledger()

    # Menu dispatch table
    menu_actions = {
        1: add_person_interactive,
        2: add_expense_interactive,
        3: view_people,
        4: view_expenses,
        5: view_balances,
        6: show_summary,
        7: settle_debts,
    }

    while True:
        print_menu()
        choice = get_user_choice()

        if choice == 8:  # Exit
            print("\n👋 Thank you for using the Expense Splitting Calculator!")
            print("Have a great day! 💰")
            break

        # Execute the chosen action
        if choice in menu_actions:
            menu_actions[choice](ledger)


if __name__ == "__main__":
    main()
