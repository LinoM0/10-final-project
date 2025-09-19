# 💰 Expense Splitting Calculator

**CS50P Final Project**

A comprehensive Python application for splitting shared expenses among friends, family, or colleagues with mathematical precision and multiple splitting strategies.

## 🌟 Features

### Core Functionality
- **Multiple Split Strategies**: Equal, weighted, percentage-based, and exact amount splits
- **Interactive Interface**: Professionally organized CLI with clear menu structure
- **Smart Settlement**: Optimized minimal transaction settlement algorithm
- **Modular Architecture**: Clean separation with constants, utils, models, and strategies

### Split Strategies
1. **Equal Split**: Divide expenses equally among all participants
2. **Weighted Split**: Split based on custom weights (e.g., by income, usage)
3. **Percentage Split**: Specify exact percentages for each person (must sum to 100%)
4. **Exact Amount Split**: Define precise amounts for each participant

### User Experience
- 🎨 Clean, emoji-enhanced interface with improved navigation
- 📊 Comprehensive balance tracking with professional formatting
- ⚡ Enhanced input validation with centralized constants configuration
- 🔄 Interactive menu-driven workflow with logical organization
- 💡 Clear feedback and confirmation messages
- 🛡️ Robust type checking and comprehensive error handling
- 🏗️ Modular codebase structure for maintainability and testing

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.9+ required
# Install dependencies
pip install inflect pytest
```

### Running the Application
```bash
# Interactive mode
python project.py

# Run tests
pytest -v ./tests
```

## 📖 Usage Examples

### Basic Workflow
1. **Add People**: Start by adding participants to your ledger
2. **Add Expenses**: Record who paid what and how to split it
3. **View Balances**: Check current balances and who owes what
4. **Settle Debts**: Get minimal transactions to balance everyone out

### Example Scenario
```
🏷️ Restaurant Bill: £120
- Paid by: Alice
- Split equally among: Alice, Bob, Charlie
- Result: Each owes £40

💳 Taxi Ride: £30  
- Paid by: Bob
- Split by weights: Alice(2), Bob(1), Charlie(1)
- Result: Alice owes £15, Bob owes £7.50, Charlie owes £7.50
```

## 🏗️ Architecture

### Project Structure
```
expense-splitting-calculator/
├── project.py              # Main interactive CLI application
├── ledger.py               # Core ledger management logic
├── models.py               # Person and Expense data models
├── split_strategies.py     # Split calculation algorithms  
├── utils.py                # Utility functions and validation
├── constants.py            # Application constants and configuration
├── tests/                  # Comprehensive test suite (94 tests)
│   ├── test_ledger.py
│   ├── test_models.py
│   ├── test_split_strategies.py
│   ├── test_integration.py
│   └── conftest.py
├── pytest.ini             # Test configuration
└── README.md              # This documentation
```

### Key Classes
- **`Ledger`**: Central management of people and expenses with enhanced validation
- **`Person`**: Individual with balance, paid, and owed amounts
- **`Expense`**: Single expense with payer, amount, and split strategy
- **`Split`**: Abstract base for splitting algorithms
- **`EqualSplit`, `WeightsSplit`, etc.**: Concrete splitting implementations

## 🧪 Testing

Comprehensive test suite with 94 tests covering:
- **Unit Tests**: Individual components (Person, Expense, Split strategies)
- **Integration Tests**: Complete workflows and edge cases
- **Error Handling**: Invalid inputs and boundary conditions
- **Precision Tests**: Mathematical accuracy verification

## 🎯 Design Principles

1. **Separation of Concerns**: Clear separation between data models, business logic, and UI
2. **Strategy Pattern**: Pluggable split algorithms for extensibility
3. **Enhanced Input Validation**: Robust validation with descriptive error messages
4. **User Experience**: Intuitive interface with helpful feedback and smart formatting
5. **Mathematical Accuracy**: Precision-focused calculations with edge case handling
6. **Test Coverage**: Comprehensive testing for reliability
7. **Performance Optimization**: Efficient algorithms
8. **Code Quality**: Modular design with utility functions and constants

## 🔧 Customization

### Adding New Split Strategies
1. Inherit from `Split` base class
2. Implement `compute_shares()` method
3. Add to `Expense` class constructor
4. Write comprehensive tests

### Example Custom Split
```python
class CustomSplit(Split):
    def compute_shares(self, amount, participants):
        # Your custom logic here
        return {participant: share for participant, share in mapping}
```

## 🤝 Contributing

This is a CS50P final project, but suggestions for improvements are welcome:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 🎓 Educational Value

This project demonstrates:
- **Object-Oriented Programming**: Classes, inheritance, encapsulation with enhanced data models
- **Design Patterns**: Strategy pattern for split algorithms with abstract base classes
- **Modular Architecture**: Professional code organization with constants, utils, models separation
- **Testing**: Comprehensive unit and integration testing with pytest (94 tests)
- **Error Handling**: Robust exception handling with centralized validation
- **User Interface**: Professional interactive CLI with organized menu system
- **Mathematical Computing**: Precision handling in financial calculations with consistent formatting
- **Code Quality**: Clean architecture, utility functions, comprehensive documentation
- **Configuration Management**: Centralized constants for maintainable configuration

## 📋 Requirements

- Python 3.9+
- `inflect` library (for natural language joining)
- `pytest` (for running tests)

## 📄 License

MIT License - Feel free to use this code for educational purposes.

---

**Created as part of CS50P (Harvard's Introduction to Programming with Python)**

*This expense splitting calculator solves real-world problems while demonstrating advanced Python programming concepts including object-oriented design, mathematical precision, comprehensive testing, and user experience design.*