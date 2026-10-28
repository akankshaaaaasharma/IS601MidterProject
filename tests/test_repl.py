from decimal import Decimal
from unittest.mock import patch

import pytest

from app.calculator_repl import calculator_repl
from app.exceptions import OperationError, ValidationError


def run_repl(inputs):
    with patch("builtins.input", side_effect=inputs):
        calculator_repl()


@pytest.fixture
def calc():
    """Replace Calculator and the observers so nothing touches disk."""
    with patch("app.calculator_repl.Calculator") as mock_calculator, \
         patch("app.calculator_repl.LoggingObserver"), \
         patch("app.calculator_repl.AutoSaveObserver"):
        yield mock_calculator.return_value


# exit

def test_exit_saves_history(calc, capsys):
    run_repl(["exit"])
    out = capsys.readouterr().out
    calc.save_history.assert_called_once()
    assert "History saved successfully." in out
    assert "Goodbye!" in out


def test_exit_save_failure_still_exits(calc, capsys):
    calc.save_history.side_effect = Exception("disk full")
    run_repl(["exit"])
    out = capsys.readouterr().out
    assert "Warning: Could not save history: disk full" in out
    assert "Goodbye!" in out


# help and unknown

def test_help(calc, capsys):
    run_repl(["help", "exit"])
    assert "Available commands:" in capsys.readouterr().out


def test_unknown_command(calc, capsys):
    run_repl(["banana", "exit"])
    assert "Unknown command: 'banana'" in capsys.readouterr().out


# history

def test_history_empty(calc, capsys):
    calc.show_history.return_value = []
    run_repl(["history", "exit"])
    assert "No calculations in history" in capsys.readouterr().out


def test_history_with_entries(calc, capsys):
    calc.show_history.return_value = ["Addition(2, 3) = 5", "Subtraction(5, 1) = 4"]
    run_repl(["history", "exit"])
    out = capsys.readouterr().out
    assert "Calculation History:" in out
    assert "1. Addition(2, 3) = 5" in out
    assert "2. Subtraction(5, 1) = 4" in out


# clear

def test_clear(calc, capsys):
    run_repl(["clear", "exit"])
    calc.clear_history.assert_called_once()
    assert "History cleared" in capsys.readouterr().out


# undo / redo

@pytest.mark.parametrize("command, method, success_msg, fail_msg", [
    ("undo", "undo", "Operation undone", "Nothing to undo"),
    ("redo", "redo", "Operation redone", "Nothing to redo"),
])
@pytest.mark.parametrize("succeeds", [True, False])
def test_undo_redo(calc, capsys, command, method, success_msg, fail_msg, succeeds):
    getattr(calc, method).return_value = succeeds
    run_repl([command, "exit"])
    out = capsys.readouterr().out
    assert (success_msg if succeeds else fail_msg) in out


# save / load

def test_save_success(calc, capsys):
    run_repl(["save", "exit"])
    assert "History saved successfully" in capsys.readouterr().out


def test_save_error(calc, capsys):
    calc.save_history.side_effect = Exception("no permission")
    run_repl(["save", "exit"])
    assert "Error saving history: no permission" in capsys.readouterr().out


def test_load_success(calc, capsys):
    run_repl(["load", "exit"])
    calc.load_history.assert_called_once()
    assert "History loaded successfully" in capsys.readouterr().out


def test_load_error(calc, capsys):
    calc.load_history.side_effect = Exception("bad csv")
    run_repl(["load", "exit"])
    assert "Error loading history: bad csv" in capsys.readouterr().out


# operations

@pytest.mark.parametrize("command", ["add", "subtract", "multiply", "divide", "power", "root"])
def test_operation_success(calc, capsys, command):
    calc.perform_operation.return_value = Decimal("5.00")
    run_repl([command, "2", "3", "exit"])
    calc.set_operation.assert_called_once()
    calc.perform_operation.assert_called_once_with("2", "3")
    assert "Result: 5" in capsys.readouterr().out


def test_operation_non_decimal_result(calc, capsys):
    calc.perform_operation.return_value = 7
    run_repl(["add", "3", "4", "exit"])
    assert "Result: 7" in capsys.readouterr().out


def test_cancel_at_first_number(calc, capsys):
    run_repl(["add", "cancel", "exit"])
    calc.perform_operation.assert_not_called()
    assert "Operation cancelled" in capsys.readouterr().out


def test_cancel_at_second_number(calc, capsys):
    run_repl(["add", "2", "CANCEL", "exit"])
    calc.perform_operation.assert_not_called()
    assert "Operation cancelled" in capsys.readouterr().out


@pytest.mark.parametrize("error", [ValidationError("bad input"), OperationError("div by zero")])
def test_operation_known_errors(calc, capsys, error):
    calc.perform_operation.side_effect = error
    run_repl(["divide", "1", "0", "exit"])
    assert f"Error: {error}" in capsys.readouterr().out


def test_operation_unexpected_error(calc, capsys):
    calc.perform_operation.side_effect = RuntimeError("weird")
    run_repl(["add", "1", "2", "exit"])
    assert "Unexpected error: weird" in capsys.readouterr().out


# loop level exceptions

def test_keyboard_interrupt_continues(calc, capsys):
    run_repl([KeyboardInterrupt(), "exit"])
    out = capsys.readouterr().out
    assert "Operation cancelled" in out
    assert "Goodbye!" in out


def test_eof_exits(calc, capsys):
    run_repl([EOFError()])
    assert "Input terminated. Exiting..." in capsys.readouterr().out


def test_generic_error_in_loop_continues(calc, capsys):
    run_repl([Exception("odd"), "exit"])
    out = capsys.readouterr().out
    assert "Error: odd" in out
    assert "Goodbye!" in out


def test_fatal_error_is_reraised(capsys):
    with patch("app.calculator_repl.Calculator", side_effect=Exception("boom")):
        with pytest.raises(Exception, match="boom"):
            calculator_repl()
    assert "Fatal error: boom" in capsys.readouterr().out