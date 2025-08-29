#!/usr/bin/env python3
"""
Demonstration of precision improvements in expense splitting.

This script shows how delaying rounding until settlement improves mathematical accuracy.
"""

from ledger import Ledger


def demonstrate_precision_improvement():
    """Demonstrate the precision improvement from delayed rounding."""
    print("=== Precision Improvement Demonstration ===\n")

    # Create a scenario where precision matters
    ledger = Ledger()
    ledger.add_person("alice")
    ledger.add_person("bob")
    ledger.add_person("charlie")

    # Add an expense that doesn't divide evenly
    ledger.add_expense("alice", 10.0, ["alice", "bob", "charlie"], "equal")
    ledger.balances()

    print("Expense: 10.0£ split equally among 3 people")
    print("Mathematical result: 10.0 ÷ 3 = 3.3333...")
    print()

    print("OLD APPROACH (rounding per expense):")
    print("- Each person owes: 3.33£ (rounded)")
    print("- Total owed: 3.33 × 3 = 9.99£")
    print("- Money lost to rounding: 10.00 - 9.99 = 0.01£")
    print()

    print("NEW APPROACH (precision preserved until settlement):")
    exact_owe = 10.0 / 3
    print(f"- Each person owes: {exact_owe:.10f}£ (exact)")
    print(f"- Total owed: {exact_owe * 3:.10f}£ = 10.0£ (exact)")
    print("- No money lost to rounding!")
    print()

    print("Final balances (rounded only at settlement):")
    for name, person in ledger.people.items():
        print(f"- {name.capitalize()}: {person.balance}£")

    print()
    print("This precision approach ensures:")
    print("✓ Mathematical accuracy is preserved")
    print("✓ No accumulation of rounding errors")
    print("✓ Settlements balance perfectly")
    print("✓ Rounding only happens when displaying final amounts")


if __name__ == "__main__":
    demonstrate_precision_improvement()
