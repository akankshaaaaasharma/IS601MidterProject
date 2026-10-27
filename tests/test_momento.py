import pytest
from decimal import Decimal
from datetime import datetime
from app.calculation import Calculation
from app.calculator_momento import CalculatorMemento
from app.exceptions import OperationError

@pytest.fixture
def sample_history():
    return [
        Calculation(operation="Addition", operand1=Decimal("2"), operand2=Decimal("3")),
        Calculation(operation="Multiplication", operand1=Decimal("4"), operand2=Decimal("2.5")),
    ]


def test_memento_stores_history(sample_history):
    memento = CalculatorMemento(history=sample_history)
    assert memento.history == sample_history


def test_memento_default_timestamp(sample_history):
    before = datetime.now()
    memento = CalculatorMemento(history=sample_history)
    after = datetime.now()
    assert before <= memento.timestamp <= after


def test_memento_custom_timestamp(sample_history):
    timestamp = datetime(2024, 1, 1, 12, 0, 0)
    memento = CalculatorMemento(history=sample_history, timestamp=timestamp)
    assert memento.timestamp == timestamp


def test_memento_snapshot_is_independent_of_original_list(sample_history):
    memento = CalculatorMemento(history=sample_history.copy())
    sample_history.append(
        Calculation(operation="Subtraction", operand1=Decimal("9"), operand2=Decimal("1"))
    )
    assert len(memento.history) == 2


def test_to_dict(sample_history):
    timestamp = datetime(2024, 1, 1, 12, 0, 0)
    memento = CalculatorMemento(history=sample_history, timestamp=timestamp)
    assert memento.to_dict() == {
        "history": [calc.to_dict() for calc in sample_history],
        "timestamp": "2024-01-01T12:00:00",
    }


def test_to_dict_empty_history():
    timestamp = datetime(2024, 1, 1, 12, 0, 0)
    memento = CalculatorMemento(history=[], timestamp=timestamp)
    assert memento.to_dict() == {"history": [], "timestamp": "2024-01-01T12:00:00"}


def test_from_dict(sample_history):
    data = {
        "history": [calc.to_dict() for calc in sample_history],
        "timestamp": "2024-01-01T12:00:00",
    }
    memento = CalculatorMemento.from_dict(data)
    assert memento.history == sample_history
    assert memento.timestamp == datetime(2024, 1, 1, 12, 0, 0)


def test_from_dict_empty_history():
    data = {"history": [], "timestamp": "2024-01-01T12:00:00"}
    memento = CalculatorMemento.from_dict(data)
    assert memento.history == []


def test_round_trip(sample_history):
    original = CalculatorMemento(history=sample_history)
    restored = CalculatorMemento.from_dict(original.to_dict())
    assert restored.history == original.history
    assert restored.timestamp == original.timestamp
    for restored_calc, original_calc in zip(restored.history, original.history):
        assert restored_calc.timestamp == original_calc.timestamp


def test_from_dict_missing_history_key():
    with pytest.raises(KeyError):
        CalculatorMemento.from_dict({"timestamp": "2024-01-01T12:00:00"})


def test_from_dict_missing_timestamp_key(sample_history):
    with pytest.raises(KeyError):
        CalculatorMemento.from_dict({"history": [c.to_dict() for c in sample_history]})


def test_from_dict_invalid_timestamp():
    with pytest.raises(ValueError):
        CalculatorMemento.from_dict({"history": [], "timestamp": "not-a-date"})


def test_from_dict_invalid_calculation_data():
    data = {
        "history": [
            {
                "operation": "Addition",
                "operand1": "invalid",
                "operand2": "3",
                "result": "5",
                "timestamp": datetime.now().isoformat(),
            }
        ],
        "timestamp": "2024-01-01T12:00:00",
    }
    with pytest.raises(OperationError, match="Invalid calculation data"):
        CalculatorMemento.from_dict(data)