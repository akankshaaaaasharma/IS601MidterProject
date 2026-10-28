# Advanced Calculator (IS601 Midterm Project)

A command-line calculator in Python with ten operations, undo/redo, logging, CSV auto-save, environment-based configuration, and a dynamic help menu. It uses the Factory, Memento, and Observer design patterns, plus the Decorator pattern for the help menu.

## Features

- 10 operations: add, subtract, multiply, divide, power, root, modulus, int_divide, percent, abs_diff
- Factory pattern for creating operations
- Memento pattern for undo and redo
- Observer pattern for logging and auto-save
- History saved to and loaded from CSV with pandas
- Configuration through a `.env` file with defaults
- Custom exceptions and input validation
- REPL command-line interface
- Dynamic help menu using the Decorator pattern (optional feature)
- pytest suite with over 90% coverage
- GitHub Actions CI that fails below 90% coverage

## Installation

```
git clone https://github.com/akankshaaaaasharma/IS601MidterProject.git
cd IS601MidterProject
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`. Python 3.12 is recommended.

## Configuration

Create a `.env` file in the project root:

```
CALCULATOR_LOG_DIR=logs
CALCULATOR_HISTORY_DIR=history
CALCULATOR_MAX_HISTORY_SIZE=100
CALCULATOR_AUTO_SAVE=true
CALCULATOR_PRECISION=10
CALCULATOR_MAX_INPUT_VALUE=1000000
CALCULATOR_DEFAULT_ENCODING=utf-8
```

| Variable | Purpose |
|---|---|
| CALCULATOR_LOG_DIR | Folder for log files |
| CALCULATOR_HISTORY_DIR | Folder for the history CSV |
| CALCULATOR_MAX_HISTORY_SIZE | Maximum history entries |
| CALCULATOR_AUTO_SAVE | true or false, save after each calculation |
| CALCULATOR_PRECISION | Decimal places |
| CALCULATOR_MAX_INPUT_VALUE | Largest allowed input |
| CALCULATOR_DEFAULT_ENCODING | Encoding for file operations |

Missing variables fall back to defaults, and settings are validated on startup.

## Usage

```
python main.py
```

Type `help` to see commands. Each operation asks for two numbers. Type `cancel` at either prompt to abort.

### Operations

| Command | Description | Example |
|---|---|---|
| add | a + b | 2, 3 gives 5 |
| subtract | a - b | 5, 2 gives 3 |
| multiply | a * b | 4, 3 gives 12 |
| divide | a / b, b cannot be 0 | 10, 4 gives 2.5 |
| power | a to the power b, no negative exponents | 2, 3 gives 8 |
| root | bth root of a | 27, 3 gives 3 |
| modulus | remainder of a / b | 10, 3 gives 1 |
| int_divide | a // b | 7, 2 gives 3 |
| percent | (a / b) * 100 | 1, 4 gives 25 |
| abs_diff | absolute value of a - b | 3, 10 gives 7 |

### Other commands

| Command | Description |
|---|---|
| history | Show all calculations |
| clear | Clear history |
| undo | Undo the last calculation |
| redo | Redo the last undone calculation |
| save | Save history to CSV |
| load | Load history from CSV |
| help | Show available commands |
| exit | Save and quit |

## Design Patterns

- **Factory:** `OperationFactory` creates operation objects from a command name.
- **Memento:** snapshots of the history make undo and redo possible.
- **Observer:** `LoggingObserver` logs each calculation, and `AutoSaveObserver` saves history to CSV with pandas.
- **Decorator:** the help menu reads the operations registered in the factory, so new operations appear in help automatically.

## Error Handling and Logging

Custom exceptions (`OperationError`, `ValidationError`) separate bad input from failed operations. Inputs must be numeric and within the configured maximum. Missing or malformed CSV files are handled with clear messages. Logging uses Python's `logging` module with INFO, WARNING, and ERROR levels, written to a file in the log directory.

## Testing

```
pytest
```

Coverage is enabled in `pytest.ini`. To see missed lines:

```
pytest --cov=app --cov-report=term-missing
```

Tests cover normal and edge cases such as division by zero, negative exponents, empty history, and malformed CSV files.

## Continuous Integration

GitHub Actions (`.github/workflows/python-app.yml`) runs on every push and pull request to `main`. It installs dependencies from `requirements.txt` and runs:

```
pytest --cov=app --cov-fail-under=90
```

The build fails if coverage drops below 90%.