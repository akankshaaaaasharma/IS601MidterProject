from abc import ABC, abstractmethod
from decimal import Decimal
from email.mime import base
from typing import Dict
#from app.exceptions import OperationError, UnknownOperationError, ValidationError
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
    def execute(self, a, b):
        self.validate_operands(a, b)
        return str(a + b)

class Subtraction(Operation):
    def execute(self, a, b):
        self.validate_operands(a, b)
        return str(a - b)

class Multiplication(Operation):
    def execute(self, a, b):
        return str(a * b)

class Division(Operation):
    def execute(self, a, b):
        self.validate_operands(a, b)
        return str(a / b)

    def validate_operands(self, a, b):
        if b == 0:
            raise ValueError("Division by zero is not allowed")

class Power(Operation):
    def execute(self, a, b):
        return str(a**b)
    
class Modulus(Operation):
    def execute(self, a, b):
        self.validate_operands(a, b)
        return str(a % b)

    def validate_operands(self, a, b):
        super().validate_operands(a, b)
        if b == 0:
            raise ValueError("Modulus by zero is not allowed")

class Root(Operation):
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        self.validate_operands(a, b)
        root_degree = float(a)

        if a < 0 and root_degree % 2 != 0:
            abs_base = abs(base)
            result = math.pow(abs_base, 1 / root_degree)
            return str(-result)

        try:
            result = math.pow(base, 1 / root_degree)
            return str(result)
        except ValueError as e:
            raise ValueError(f"Error computing root: {e}")

        def validate_operands(self, a: Decimal, b: Decimal) -> None:
            if b == 0:
                raise ValueError("Zero root is undefined")

            if b % 1 != 0:
                raise ValueError("Root degree must be an integer.")

            if a < 0 and b % 2 == 0:
                raise ValueError("Cannot calculate even root of a negative number")

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
            raise ValidationError("Division by zero is not allowed")