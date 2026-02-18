"""
Example: TDD Feature Implementation

Demonstrates how to implement a feature using CodeBot's TDD workflow.
"""

import asyncio
import tempfile
import os
from src.superpowers.tdd import TDDExpert


async def main():
    tdd = TDDExpert()

    # Step 1: Define the feature
    feature = "Calculator that adds, subtracts, multiplies, and divides"

    # Step 2: Write the test
    test_code = '''
def test_add():
    from calculator import Calculator
    calc = Calculator()
    assert calc.add(2, 3) == 5

def test_subtract():
    from calculator import Calculator
    calc = Calculator()
    assert calc.subtract(5, 3) == 2

def test_multiply():
    from calculator import Calculator
    calc = Calculator()
    assert calc.multiply(4, 3) == 12

def test_divide():
    from calculator import Calculator
    calc = Calculator()
    assert calc.divide(10, 2) == 5.0

def test_divide_by_zero():
    from calculator import Calculator
    calc = Calculator()
    try:
        calc.divide(10, 0)
        assert False, "Should raise ValueError"
    except ValueError:
        pass
'''

    # Step 3: Write the implementation
    impl_code = '''
class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b

    def multiply(self, a, b):
        return a * b

    def divide(self, a, b):
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
'''

    # Step 4: Execute TDD cycle
    result = tdd.execute_cycle(feature, test_code, impl_code)

    print(f"🔴 RED phase: {'PASS' if result.get('red_phase') else 'FAIL'}")
    print(f"🟢 GREEN phase: {'PASS' if result.get('green_phase') else 'FAIL'}")
    print(f"✅ Cycle complete!")
    print(f"📊 History: {len(tdd.history)} cycles")


if __name__ == "__main__":
    asyncio.run(main())
