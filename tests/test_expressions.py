"""
Test suite for core mathematical expression data structures.
"""
import pytest
from fractions import Fraction
from src.formal.expressions import Number, Variable, Operation, Fact, Rule, MathProblem


class TestNumber:
    def test_integer_creation(self):
        num = Number(5)
        assert num.value == 5
        assert str(num) == "5"
    
    def test_fraction_creation(self):
        num = Number(Fraction(3, 4))
        assert num.value == Fraction(3, 4)
        assert str(num) == "3/4"
    
    def test_float_conversion(self):
        num = Number(0.5)
        assert num.value == Fraction(1, 2)
        assert str(num) == "1/2"
    
    def test_equality(self):
        num1 = Number(5)
        num2 = Number(5)
        num3 = Number(3)
        assert num1 == num2
        assert num1 != num3
    
    def test_hash(self):
        num1 = Number(5)
        num2 = Number(5)
        assert hash(num1) == hash(num2)


class TestVariable:
    def test_creation(self):
        var = Variable("x")
        assert var.name == "x"
        assert str(var) == "x"
    
    def test_invalid_names(self):
        with pytest.raises(ValueError):
            Variable("")
        with pytest.raises(ValueError):
            Variable("x+")
        with pytest.raises(ValueError):
            Variable("2x")
    
    def test_equality(self):
        var1 = Variable("x")
        var2 = Variable("x")
        var3 = Variable("y")
        assert var1 == var2
        assert var1 != var3


class TestOperation:
    def test_creation(self):
        x = Variable("x")
        three = Number(3)
        op = Operation(x, "+", three)
        assert op.left == x
        assert op.operator == "+"
        assert op.right == three
    
    def test_string_representation(self):
        x = Variable("x")
        three = Number(3)
        op = Operation(x, "+", three)
        assert str(op) == "x + 3"
    
    def test_nested_operations(self):
        x = Variable("x")
        y = Variable("y")
        two = Number(2)
        
        # x + y
        sum_op = Operation(x, "+", y)
        # (x + y) * 2
        mult_op = Operation(sum_op, "*", two)
        assert str(mult_op) == "(x + y) * 2"
    
    def test_invalid_operator(self):
        x = Variable("x")
        three = Number(3)
        with pytest.raises(ValueError):
            Operation(x, "invalid", three)


class TestFact:
    def test_equality_fact(self):
        x = Variable("x")
        five = Number(5)
        fact = Fact("eq", [x, five])
        assert fact.predicate == "eq"
        assert fact.arguments == [x, five]
        assert str(fact) == "eq(x, 5)"
    
    def test_unary_predicate(self):
        n = Variable("n")
        fact = Fact("even", [n])
        assert str(fact) == "even(n)"
    
    def test_invalid_predicate(self):
        x = Variable("x")
        with pytest.raises(ValueError):
            Fact("invalid", [x])
    
    def test_wrong_argument_count(self):
        x = Variable("x")
        y = Variable("y")
        # eq needs exactly 2 arguments
        with pytest.raises(ValueError):
            Fact("eq", [x, y, x])
        # even needs exactly 1 argument
        with pytest.raises(ValueError):
            Fact("even", [x, y])


class TestRule:
    def test_simple_rule(self):
        # Rule: eq(X + A, B) → eq(X, B - A)
        X = Variable("X")
        A = Variable("A")
        B = Variable("B")
        
        premise = Fact("eq", [Operation(X, "+", A), B])
        conclusion = Fact("eq", [X, Operation(B, "-", A)])
        
        rule = Rule([premise], conclusion, "subtraction_property")
        assert rule.name == "subtraction_property"
        assert len(rule.premises) == 1
        assert rule.conclusion == conclusion
    
    def test_multiple_premises(self):
        # Rule: eq(X, Y) ∧ eq(Y, Z) → eq(X, Z)
        X = Variable("X")
        Y = Variable("Y")
        Z = Variable("Z")
        
        premise1 = Fact("eq", [X, Y])
        premise2 = Fact("eq", [Y, Z])
        conclusion = Fact("eq", [X, Z])
        
        rule = Rule([premise1, premise2], conclusion, "transitivity")
        assert len(rule.premises) == 2


class TestMathProblem:
    def test_creation(self):
        # Problem: If x + 3 = 7, find x
        x = Variable("x")
        three = Number(3)
        seven = Number(7)
        four = Number(4)
        
        # Fact: eq(x + 3, 7)
        fact = Fact("eq", [Operation(x, "+", three), seven])
        
        # Rule: eq(X + A, B) → eq(X, B - A)
        X = Variable("X")
        A = Variable("A")
        B = Variable("B")
        premise = Fact("eq", [Operation(X, "+", A), B])
        conclusion = Fact("eq", [X, Operation(B, "-", A)])
        rule = Rule([premise], conclusion, "subtraction")
        
        # Goal: eq(x, 4)
        goal = Fact("eq", [x, four])
        
        problem = MathProblem([fact], [rule], goal, "If x + 3 = 7, find x")
        assert len(problem.facts) == 1
        assert len(problem.rules) == 1
        assert problem.goal == goal
        assert problem.original_text == "If x + 3 = 7, find x"
    
    def test_validation(self):
        x = Variable("x")
        fact = Fact("eq", [x, Number(5)])
        goal = Fact("eq", [x, Number(5)])
        
        problem = MathProblem([fact], [], goal)
        assert problem.validate() == True


if __name__ == "__main__":
    pytest.main([__file__])