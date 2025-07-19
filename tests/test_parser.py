"""
Test suite for mathematical expression and predicate parser.
"""
import pytest
from src.formal.parser import ExpressionParser, PredicateParser, RuleParser, MathParser
from src.formal.expressions import Number, Variable, Operation, Fact, Rule


class TestExpressionParser:
    def setUp(self):
        self.parser = ExpressionParser()
    
    def test_number_parsing(self):
        parser = ExpressionParser()
        
        # Integer
        expr = parser.parse_expression("5")
        assert isinstance(expr, Number)
        assert expr.value == 5
        
        # Negative integer
        expr = parser.parse_expression("-3")
        assert isinstance(expr, Number)
        assert expr.value == -3
        
        # Fraction - this will be parsed as an operation 1 / 2
        expr = parser.parse_expression("1/2")
        assert isinstance(expr, Operation)
        assert expr.operator == "/"
    
    def test_variable_parsing(self):
        parser = ExpressionParser()
        
        expr = parser.parse_expression("x")
        assert isinstance(expr, Variable)
        assert expr.name == "x"
        
        expr = parser.parse_expression("abc")
        assert isinstance(expr, Variable)
        assert expr.name == "abc"
    
    def test_simple_operations(self):
        parser = ExpressionParser()
        
        # Addition - SymPy may reorder terms
        expr = parser.parse_expression("x + 3")
        assert isinstance(expr, Operation)
        assert expr.operator == "+"
        # Check that we have one Variable and one Number in either order
        types = {type(expr.left), type(expr.right)}
        assert Variable in types
        assert Number in types
        
        # Subtraction
        expr = parser.parse_expression("a - b")
        assert isinstance(expr, Operation)
        assert expr.operator == "-"  # With evaluate=False, should preserve subtraction
        
        # Multiplication - SymPy may reorder factors
        expr = parser.parse_expression("2 * x")
        assert isinstance(expr, Operation)
        assert expr.operator == "*"
        types = {type(expr.left), type(expr.right)}
        assert Variable in types
        assert Number in types
        
        # Division  
        expr = parser.parse_expression("x / 2")
        assert isinstance(expr, Operation)
        assert expr.operator == "/"  # With evaluate=False, should preserve division
    
    def test_complex_expressions(self):
        parser = ExpressionParser()
        
        # Nested operations
        expr = parser.parse_expression("(x + 3) * 2")
        assert isinstance(expr, Operation)
        assert expr.operator == "*"
        assert isinstance(expr.left, Operation)  # x + 3
        
        # Multiple operations
        expr = parser.parse_expression("x + y - z")
        assert isinstance(expr, Operation)
        # Should be parsed as (x + y) - z
    
    def test_power_operations(self):
        parser = ExpressionParser()
        
        expr = parser.parse_expression("x^2")
        assert isinstance(expr, Operation)
        assert expr.operator == "^"
        
        # Test ** conversion to ^
        expr = parser.parse_expression("x**2")
        assert isinstance(expr, Operation)
        assert expr.operator == "^"
    
    def test_invalid_expressions(self):
        parser = ExpressionParser()
        
        with pytest.raises(ValueError):
            parser.parse_expression("")
        
        with pytest.raises(ValueError):
            parser.parse_expression("x +")


class TestPredicateParser:
    def test_binary_predicates(self):
        parser = PredicateParser()
        
        # Equality
        fact = parser.parse_fact("eq(x, 5)")
        assert fact.predicate == "eq"
        assert len(fact.arguments) == 2
        assert isinstance(fact.arguments[0], Variable)
        assert isinstance(fact.arguments[1], Number)
        
        # Greater than
        fact = parser.parse_fact("gt(a, b)")
        assert fact.predicate == "gt"
        assert len(fact.arguments) == 2
        
        # Complex expressions as arguments
        fact = parser.parse_fact("eq(x + 3, 7)")
        assert fact.predicate == "eq"
        assert isinstance(fact.arguments[0], Operation)
        assert isinstance(fact.arguments[1], Number)
    
    def test_unary_predicates(self):
        parser = PredicateParser()
        
        fact = parser.parse_fact("even(n)")
        assert fact.predicate == "even"
        assert len(fact.arguments) == 1
        assert isinstance(fact.arguments[0], Variable)
        
        fact = parser.parse_fact("odd(x)")
        assert fact.predicate == "odd"
        assert len(fact.arguments) == 1
    
    def test_nested_expressions(self):
        parser = PredicateParser()
        
        # Complex nested expression
        fact = parser.parse_fact("eq((x + 1) * 2, y - 3)")
        assert fact.predicate == "eq"
        assert len(fact.arguments) == 2
        assert isinstance(fact.arguments[0], Operation)  # (x + 1) * 2
        assert isinstance(fact.arguments[1], Operation)  # y - 3
    
    def test_invalid_predicates(self):
        parser = PredicateParser()
        
        with pytest.raises(ValueError):
            parser.parse_fact("invalid_format")
        
        with pytest.raises(ValueError):
            parser.parse_fact("eq(x")  # Missing closing parenthesis
        
        with pytest.raises(ValueError):
            parser.parse_fact("unknown_pred(x, y)")  # Unknown predicate


class TestRuleParser:
    def test_simple_rule(self):
        parser = RuleParser()
        
        # Single premise rule
        rule = parser.parse_rule("eq(X + A, B) → eq(X, B - A)", "subtraction")
        assert rule.name == "subtraction"
        assert len(rule.premises) == 1
        assert rule.premises[0].predicate == "eq"
        assert rule.conclusion.predicate == "eq"
    
    def test_multiple_premises(self):
        parser = RuleParser()
        
        # Multiple premises with ∧
        rule = parser.parse_rule("eq(X, Y) ∧ eq(Y, Z) → eq(X, Z)", "transitivity")
        assert rule.name == "transitivity"
        assert len(rule.premises) == 2
        assert rule.premises[0].predicate == "eq"
        assert rule.premises[1].predicate == "eq"
        assert rule.conclusion.predicate == "eq"
    
    def test_complex_rule(self):
        parser = RuleParser()
        
        # Rule with complex expressions
        rule = parser.parse_rule("even(X) ∧ gt(X, 0) → even(X * 2)")
        assert len(rule.premises) == 2
        assert rule.premises[0].predicate == "even"
        assert rule.premises[1].predicate == "gt"
        assert rule.conclusion.predicate == "even"
    
    def test_invalid_rules(self):
        parser = RuleParser()
        
        with pytest.raises(ValueError):
            parser.parse_rule("invalid rule format")
        
        with pytest.raises(ValueError):
            parser.parse_rule("eq(X, Y) →")  # Missing conclusion


class TestMathParser:
    def test_integration(self):
        parser = MathParser()
        
        # Test parsing expressions
        expr = parser.parse_expression("x + 3")
        assert isinstance(expr, Operation)
        
        # Test parsing facts
        fact = parser.parse_fact("eq(x, 5)")
        assert isinstance(fact, Fact)
        
        # Test parsing rules
        rule = parser.parse_rule("eq(X, Y) → gt(X, 0)")
        assert isinstance(rule, Rule)
    
    def test_parse_lists(self):
        parser = MathParser()
        
        # Parse multiple facts
        facts = parser.parse_facts_list([
            "eq(x, 5)",
            "gt(y, 0)",
            "even(n)"
        ])
        assert len(facts) == 3
        assert all(isinstance(f, Fact) for f in facts)
        
        # Parse multiple rules
        rules = parser.parse_rules_list([
            "eq(X + A, B) → eq(X, B - A)",
            "gt(X, Y) ∧ gt(Y, Z) → gt(X, Z)"
        ], ["subtraction", "transitivity"])
        assert len(rules) == 2
        assert all(isinstance(r, Rule) for r in rules)
        assert rules[0].name == "subtraction"
        assert rules[1].name == "transitivity"


if __name__ == "__main__":
    pytest.main([__file__])