from abc import ABC, abstractmethod
from decimal import Decimal
from email.mime import base
from typing import Dict

from app.exceptions import ValidationError
import math


class Operation(ABC):
    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> str:
        pass

    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        pass

    def __str__(self):
        return self.__class__.__name__

class Addition(Operation):
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a + b

class Subtraction(Operation):
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a - b

class Multiplication(Operation):
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a * b

class Division(Operation):
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b == 0:
            raise ValidationError("Division by zero is not allowed")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return a / b

class Power(Operation):
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if b < 0:
            raise ValidationError("Negative exponents not supported")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(pow(float(a), float(b)))

    
class Modulus(Operation):
    def execute(self, a, b):
        self.validate_operands(a, b)
        return str(a % b)

    def validate_operands(self, a, b):
        super().validate_operands(a, b)
        if b == 0:
            raise ValueError("Modulus by zero is not allowed")

class Root(Operation):
    def validate_operands(self, a: Decimal, b: Decimal) -> None:
        super().validate_operands(a, b)
        if a < 0:
            raise ValidationError("Cannot calculate root of negative number")
        if b == 0:
            raise ValidationError("Zero root is undefined")

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        return Decimal(pow(float(a), 1 / float(b)))

class Percentage(Operation):
    def validate_operands(self, a, b):
        super().validate_operands(a, b)
        if b==0:
            raise ValueError("Division by zero is not allowed")
        
    def execute(self, a, b):
        result = a/b*100
        return str(result.quantize(Decimal('1.00'))) + '%'        

class AbsDiff(Operation):
    def execute(self, a, b):
        return str(abs(a-b))

class Int_Division(Operation):
    def execute(self, a, b):
        self.validate_operands(a,b)
        return str(a//b)
    
    def validate_operands(self, a, b):
        super().validate_operands(a, b)
        if b==0:
            raise ValueError("Division by zero is not allowed")

class OperationFactory:
    _operations: Dict[str, type] = {
        'add': Addition,
        'subtract': Subtraction,
        'multiply': Multiplication,
        'divide': Division,
        'power': Power,
        'root': Root,
        'modulus': Modulus,
        'percentage': Percentage,
        'absdiff': AbsDiff,
        'int_division': Int_Division
    }

    @classmethod
    def register_operation(cls, name: str, operation_class: type) -> None:
        if not issubclass(operation_class, Operation):
            raise TypeError("Operation class must inherit from Operation")
        cls._operations[name.lower()] = operation_class

    @classmethod
    def create_operation(cls, operation_type: str) -> Operation:
        operation_class = cls._operations.get(operation_type.lower())
        if not operation_class:
            raise ValueError(f"Unknown operation: {operation_type}")
        return operation_class()