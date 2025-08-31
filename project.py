#!/usr/bin/env python3
"""
Interactive Expense Splitting Application

This application allows users to interactively manage shared expenses
among a group of people through a command-line interface.
"""

from ledger import Ledger
from models import is_valid_money
from utils import (
    format_currency, 
    clean_input, 
    validate_name, 
    parse_amount_input, 
    generate_expense_summary,
    format_transaction_list
)


def print_banner():
    """Print the application banner."""
    print("=" * 60)
    print("           💰 EXPENSE SPLITTING CALCULATOR 💰")
    print("=" * 60)
    print("Welcome! This app helps you split expenses fairly among friends.")
    print()


def print_menu():
    """Print the main menu options."""
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
    """Get and validate user menu choice."""
    while True:
        try:
            choice = input("\nEnter your choice (1-8): ").strip()
            if choice in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                return int(choice)
            else:
                print("❌ Invalid choice. Please enter a number between 1 and 8.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            exit(0)
        except ValueError:
            print("❌ Please enter a valid number.")


def get_monetary_input(prompt, min_amount=0.01, max_amount=999999.99):
    """Get and validate monetary input from user using enhanced utilities."""
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
    """Get and validate name input from user using enhanced utilities."""
    while True:
        try:
            name = input(prompt).strip()
            
            is_valid, error_msg = validate_name(name)
            
            if not is_valid:
                print(f"❌ {error_msg}")
                continue
                
            # Check for duplicates if provided
            if existing_names and clean_input(name) in [clean_input(n) for n in existing_names]:
                print(f"❌ Name '{name}' already exists.")
                continue
                
            return name
            
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            exit(0)
            print("❌ Please enter a valid number.")


def add_person_interactive(ledger):
    """Interactively add a person to the ledger."""
    print("\n➕ ADD A PERSON")
    print("─" * 20)

    while True:
        try:
            existing_names = list(ledger.people.keys())
            name = get_name_input("Enter person's name (or 'back' to return): ", existing_names)

            if name.lower() == "back":
                return

            ledger.add_person(name)
            print(f"✅ {name.capitalize()} has been added!")
            return
        except (ValueError, TypeError) as e:
            print(f"❌ Error: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")


def get_participants(ledger):
    """Get participants for an expense - wrapper function."""
    return get_participants_interactive(ledger)


def get_split_type():
    """Get split type from user."""
    print("\nChoose split method:")
    print("  1. Equal split")
    print("  2. Weighted split")
    print("  3. Percentage split")
    print("  4. Exact amount split")
    
    while True:
        try:
            choice = input("Enter choice (1-4): ").strip()
            if choice == "1":
                return "equal"
            elif choice == "2":
                return "weights"
            elif choice == "3":
                return "percent"
            elif choice == "4":
                return "exact"
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
        except (KeyboardInterrupt, EOFError):
            print("\n\n👋 Goodbye!")
            exit(0)


def get_participants_interactive(ledger):
    """Get participants for an expense interactively."""
    if not ledger.people:
        print("❌ No people available. Please add people first.")
        return None

    print("\nAvailable people:")
    people_list = list(ledger.people.keys())
    for i, person in enumerate(people_list, 1):
        print(f"  {i}. {person.capitalize()}")

    participants = []
    print(
        "\nSelect participants (enter numbers separated by commas, or 'all' for everyone):"
    )

    while True:
        selection = input("Participants: ").strip()

        if selection.lower() == "all":
            participants = people_list.copy()
            break

        try:
            # Parse comma-separated numbers
            indices = [int(x.strip()) for x in selection.split(",")]

            # Validate indices
            if all(1 <= i <= len(people_list) for i in indices):
                participants = [people_list[i - 1] for i in indices]
                break
            else:
                print(
                    f"❌ Invalid selection. Please enter numbers between 1 and {len(people_list)}."
                )
        except ValueError:
            print(
                "❌ Invalid format. Please enter numbers separated by commas (e.g., 1,2,3) or 'all'."
            )

    return participants


def get_split_details(split_type, participants):
    """Get additional details needed for specific split types."""
    if split_type == "weights":
        weights = {}
        print("\nEnter weights for each participant:")
        for participant in participants:
            while True:
                try:
                    weight = float(input(f"Weight for {participant.capitalize()}: "))
                    if weight > 0:
                        weights[participant] = weight
                        break
                    else:
                        print("❌ Weight must be positive.")
                except ValueError:
                    print("❌ Please enter a valid number.")
        return weights

    elif split_type == "percent":
        percentages = {}
        total_percent = 0
        print("\nEnter percentages for each participant (must total 100%):")
        for participant in participants:
            while True:
                try:
                    percent = float(
                        input(f"Percentage for {participant.capitalize()}: ")
                    )
                    if 0 <= percent <= 100:
                        percentages[participant] = percent
                        total_percent += percent
                        break
                    else:
                        print("❌ Percentage must be between 0 and 100.")
                except ValueError:
                    print("❌ Please enter a valid number.")

        if abs(total_percent - 100) > 0.01:
            print(f"❌ Percentages total {total_percent}%, but must total 100%.")
            return None
        return percentages

    elif split_type == "exact":
        exact_amounts = {}
        total_amount = 0
        print("\nEnter exact amounts for each participant:")
        for participant in participants:
            while True:
                try:
                    amount = float(input(f"Amount for {participant.capitalize()}: £"))
                    if amount >= 0:
                        exact_amounts[participant] = amount
                        total_amount += amount
                        break
                    else:
                        print("❌ Amount must be non-negative.")
                except ValueError:
                    print("❌ Please enter a valid number.")
        return exact_amounts, total_amount

    return None


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

        # Get amount using enhanced validation
        amount = get_monetary_input("Enter expense amount (£): ")

        # Get participants
        participants = get_participants_interactive(ledger)
        if not participants:
            print("❌ No participants selected.")
            return

        # Get split type
        split_type = get_split_type()

        # Get additional split details
        additional_args = {}
        if split_type == "weights":
            weights = get_split_details("weights", participants)
            if weights:
                additional_args = {"weights": weights}
        elif split_type == "percent":
            percentages = get_split_details("percent", participants)
            if percentages:
                additional_args = {"percentages": percentages}
        elif split_type == "exact":
            result = get_split_details("exact", participants)
            if result:
                exact_amounts, total_amount = result
                if abs(total_amount - amount) > 0.01:
                    print(f"❌ Exact amounts total £{total_amount:.2f}, but expense is £{amount:.2f}")
                    return
                additional_args = {"exact_amounts": exact_amounts}

        # Add the expense
        ledger.add_expense(payer, amount, participants, split_type, **additional_args)
        print(f"✅ Expense of £{amount:.2f} paid by {payer.capitalize()} has been added!")
        
        # Show expense summary
        print(f"   📝 Split type: {split_type.capitalize()}")
        print(f"   👥 Participants: {', '.join(p.capitalize() for p in participants)}")
        if split_type == "weights" and additional_args.get("weights"):
            print(f"   ⚖️  Weights: {additional_args['weights']}")
        elif split_type == "percent" and additional_args.get("percentages"):
            print(f"   📊 Percentages: {additional_args['percentages']}")
        elif split_type == "exact" and additional_args.get("exact_amounts"):
            print(f"   💰 Exact amounts: {additional_args['exact_amounts']}")
            
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
    """Display a comprehensive summary of the ledger."""
    print("\n� LEDGER SUMMARY")
    print("─" * 30)
    
    if not ledger.people:
        print("No people in the ledger yet.")
        input("\nPress Enter to continue...")
        return
    
    print(f"👥 People: {len(ledger.people)}")
    print(f"🧾 Expenses: {len(ledger.expenses)}")
    
    if ledger.expenses:
        total_expenses = sum(expense.amount for expense in ledger.expenses)
        print(f"💰 Total amount: £{total_expenses:.2f}")
        print(f"📈 Average expense: £{total_expenses / len(ledger.expenses):.2f}")
        
        ledger.balances()  # Calculate current balances
        
        creditors = [p for p in ledger.people.values() if p.balance > 0]
        debtors = [p for p in ledger.people.values() if p.balance < 0]
        
        if creditors:
            max_creditor = max(creditors, key=lambda p: p.balance)
            print(f"💚 Biggest creditor: {max_creditor.name.capitalize()} (+£{max_creditor.balance:.2f})")
        
        if debtors:
            max_debtor = min(debtors, key=lambda p: p.balance)
            print(f"💸 Biggest debtor: {max_debtor.name.capitalize()} (-£{abs(max_debtor.balance):.2f})")
            
        # Check if balanced
        total_balance = sum(p.balance for p in ledger.people.values())
        if abs(total_balance) < 0.01:
            print("✅ Ledger is mathematically balanced!")
        else:
            print(f"⚠️ Ledger imbalance: £{total_balance:.2f}")
    
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
    """Main interactive application loop."""
    print_banner()
    ledger = Ledger()

    while True:
        print_menu()
        choice = get_user_choice()

        if choice == 1:
            add_person_interactive(ledger)
        elif choice == 2:
            add_expense_interactive(ledger)
        elif choice == 3:
            view_people(ledger)
        elif choice == 4:
            view_expenses(ledger)
        elif choice == 5:
            view_balances(ledger)
        elif choice == 6:
            show_summary(ledger)
        elif choice == 7:
            settle_debts(ledger)
        elif choice == 8:
            print("\n👋 Thank you for using the Expense Splitting Calculator!")
            print("Have a great day! 💰")
            break


if __name__ == "__main__":
    main()
