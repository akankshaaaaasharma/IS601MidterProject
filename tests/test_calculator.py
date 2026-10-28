from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch, PropertyMock

import pandas as pd
import pytest

from app.calculator import Calculator
from app.calculator_congif import CalculatorConfig
from app.exceptions import OperationError
from app.operations import OperationFactory


@pytest.fixture
def calculator():
    with TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        config = CalculatorConfig(base_dir=temp_path)

        with patch.object(CalculatorConfig, "log_dir", new_callable=PropertyMock) as log_dir, \
             patch.object(CalculatorConfig, "log_file", new_callable=PropertyMock) as log_file, \
             patch.object(CalculatorConfig, "history_dir", new_callable=PropertyMock) as hist_dir, \
             patch.object(CalculatorConfig, "history_file", new_callable=PropertyMock) as hist_file:

            log_dir.return_value = temp_path / "logs"
            log_file.return_value = temp_path / "logs/calculator.log"
            hist_dir.return_value = temp_path / "history"
            hist_file.return_value = temp_path / "history/calculator_history.csv"

            yield Calculator(config=config)


def add(calculator, a, b):
    calculator.set_operation(OperationFactory.create_operation("add"))
    return calculator.perform_operation(a, b)


# init and logging

def test_init_survives_load_history_failure(calculator):
    with patch.object(Calculator, "load_history", side_effect=Exception("bad file")):
        new_calc = Calculator(config=calculator.config)
    assert new_calc.history == []


def test_setup_logging_failure_is_raised(calculator, capsys):
    with patch("app.calculator.logging.basicConfig", side_effect=Exception("log boom")):
        with pytest.raises(Exception, match="log boom"):
            Calculator(config=calculator.config)
    assert "Error setting up logging: log boom" in capsys.readouterr().out


# perform_operation

def test_history_is_trimmed_to_max_size(calculator):
    calculator.config.max_history_size = 2
    add(calculator, 1, 1)
    add(calculator, 2, 2)
    add(calculator, 3, 3)
    assert len(calculator.history) == 2
    assert calculator.history[0].operand1 == Decimal("2")


def test_unexpected_operation_error_is_wrapped(calculator):
    broken = Mock()
    broken.execute.side_effect = RuntimeError("kaboom")
    calculator.set_operation(broken)
    with pytest.raises(OperationError, match="Operation failed: kaboom"):
        calculator.perform_operation(1, 2)


# save history

def test_save_empty_history_writes_header_only_csv(calculator):
    calculator.save_history()
    df = pd.read_csv(calculator.config.history_file)
    assert df.empty
    assert list(df.columns) == ["operation", "operand1", "operand2", "result", "timestamp"]


def test_save_history_with_data_round_trips(calculator):
    add(calculator, 2, 3)
    calculator.save_history()
    df = pd.read_csv(calculator.config.history_file)
    assert len(df) == 1


def test_save_history_failure_raises_operation_error(calculator):
    add(calculator, 2, 3)
    with patch("app.calculator.pd.DataFrame.to_csv", side_effect=Exception("disk full")):
        with pytest.raises(OperationError, match="Failed to save history"):
            calculator.save_history()


# load history

def test_load_empty_csv_leaves_history_empty(calculator):
    calculator.save_history()  # header-only file
    calculator.load_history()
    assert calculator.history == []


def test_load_history_failure_raises_operation_error(calculator):
    calculator.save_history()  # makes sure the file exists
    with patch("app.calculator.pd.read_csv", side_effect=Exception("corrupt")):
        with pytest.raises(OperationError, match="Failed to load history"):
            calculator.load_history()


def test_load_history_restores_saved_calculations(calculator):
    add(calculator, 2, 3)
    calculator.save_history()
    calculator.history = []
    calculator.load_history()
    assert len(calculator.history) == 1


# dataframe and show_history

def test_get_history_dataframe_empty(calculator):
    assert calculator.get_history_dataframe().empty


def test_get_history_dataframe_with_data(calculator):
    add(calculator, 2, 3)
    df = calculator.get_history_dataframe()
    assert len(df) == 1
    assert {"operation", "operand1", "operand2", "result", "timestamp"} <= set(df.columns)


def test_show_history_formats_entries(calculator):
    add(calculator, 2, 3)
    lines = calculator.show_history()
    assert len(lines) == 1
    assert "(2, 3) = 5" in lines[0]


# undo / redo edge cases

def test_undo_with_nothing_returns_false(calculator):
    assert calculator.undo() is False


def test_redo_with_nothing_returns_false(calculator):
    assert calculator.redo() is False


def test_new_operation_clears_redo_stack(calculator):
    add(calculator, 1, 1)
    calculator.undo()
    add(calculator, 2, 2)
    assert calculator.redo() is False