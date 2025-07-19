"""
Test suite for pattern matching system.
"""
import pytest
from src.reasoning.pattern_matching import Substitution, PatternMatcher, RuleApplicator
from src.formal.expressions import Number, Variable, Operation, Fact, Rule


class TestSubstitution:
    def test_empty_substitution(self):
        sub = Substitution()
        assert sub.is_empty()
        assert str(sub) == "{}"
    
    def test_add_mapping(self):
        sub = Substitution()
        x = Variable("x")
        five = Number(5)
        
        assert sub.add_mapping("X", x) == True
        assert sub.get_mapping("X") == x
        
        # Adding same mapping should work
        assert sub.add_mapping("X", x) == True
        
        # Adding conflicting mapping should fail
        assert sub.add_mapping("X", five) == False
    
    def test_apply_to_expression(self):
        sub = Substitution({"X": Variable("x"), "A": Number(3)})
        
        # Variable substitution
        expr = Variable("X")
        result = sub.apply_to_expression(expr)
        assert result == Variable("x")
        
        # Number unchanged
        expr = Number(5)
        result = sub.apply_to_expression(expr)
        assert result == Number(5)
        
        # Operation substitution
        expr = Operation(Variable("X"), "+", Variable("A"))
        result = sub.apply_to_expression(expr)
        expected = Operation(Variable("x"), "+", Number(3))
        assert result == expected
    
    def test_apply_to_fact(self):
        sub = Substitution({"X": Variable("x"), "Y": Number(5)})
        
        fact = Fact("eq", [Variable("X"), Variable("Y")])
        result = sub.apply_to_fact(fact)
        expected = Fact("eq", [Variable("x"), Number(5)])
        assert result == expected
    
    def test_merge(self):
        sub1 = Substitution({"X": Variable("x")})
        sub2 = Substitution({"Y": Number(5)})
        
        # Compatible merge
        merged = sub1.merge(sub2)
        assert merged is not None
        assert merged.get_mapping("X") == Variable("x")
        assert merged.get_mapping("Y") == Number(5)
        
        # Incompatible merge
        sub3 = Substitution({"X": Number(10)})
        merged = sub1.merge(sub3)
        assert merged is None


class TestPatternMatcher:
    def test_match_numbers(self):
        matcher = PatternMatcher()
        
        # Exact match
        pattern = Number(5)
        target = Number(5)
        result = matcher.match_expression(pattern, target)
        assert result is not None
        assert result.is_empty()
        
        # No match
        pattern = Number(5)
        target = Number(3)
        result = matcher.match_expression(pattern, target)
        assert result is None
    
    def test_match_variables(self):
        matcher = PatternMatcher()
        
        # Pattern variable matches anything
        pattern = Variable("X")
        target = Number(5)
        result = matcher.match_expression(pattern, target)
        assert result is not None
        assert result.get_mapping("X") == Number(5)
        
        # Pattern variable matches another variable
        pattern = Variable("X")
        target = Variable("y")
        result = matcher.match_expression(pattern, target)
        assert result is not None
        assert result.get_mapping("X") == Variable("y")
        
        # Concrete variables must match exactly
        pattern = Variable("x")
        target = Variable("x")
        result = matcher.match_expression(pattern, target)
        assert result is not None
        assert result.is_empty()
        
        pattern = Variable("x")
        target = Variable("y")
        result = matcher.match_expression(pattern, target)
        assert result is None
    
    def test_match_operations(self):
        matcher = PatternMatcher()
        
        # Simple operation match
        pattern = Operation(Variable("X"), "+", Number(3))
        target = Operation(Variable("y"), "+", Number(3))
        result = matcher.match_expression(pattern, target)
        assert result is not None
        assert result.get_mapping("X") == Variable("y")
        
        # Different operators don't match
        pattern = Operation(Variable("X"), "+", Number(3))
        target = Operation(Variable("y"), "-", Number(3))
        result = matcher.match_expression(pattern, target)
        assert result is None
        
        # Complex nested operation
        pattern = Operation(Variable("X"), "*", Operation(Variable("Y"), "+", Number(1)))
        target = Operation(Number(2), "*", Operation(Variable("z"), "+", Number(1)))
        result = matcher.match_expression(pattern, target)
        assert result is not None
        assert result.get_mapping("X") == Number(2)
        assert result.get_mapping("Y") == Variable("z")
    
    def test_match_facts(self):
        matcher = PatternMatcher()
        
        # Simple fact match
        pattern = Fact("eq", [Variable("X"), Number(5)])
        target = Fact("eq", [Variable("y"), Number(5)])
        result = matcher.match_fact(pattern, target)
        assert result is not None
        assert result.get_mapping("X") == Variable("y")
        
        # Different predicates don't match
        pattern = Fact("eq", [Variable("X"), Number(5)])
        target = Fact("gt", [Variable("y"), Number(5)])
        result = matcher.match_fact(pattern, target)
        assert result is None
        
        # Different argument counts don't match - use even predicate (1 arg) vs eq predicate (2 args)
        pattern = Fact("eq", [Variable("X"), Number(5)])
        target = Fact("even", [Variable("y")])
        result = matcher.match_fact(pattern, target)
        assert result is None
    
    def test_match_facts_list(self):
        matcher = PatternMatcher()
        
        # Single pattern
        patterns = [Fact("eq", [Variable("X"), Number(5)])]
        targets = {
            Fact("eq", [Variable("a"), Number(5)]),
            Fact("eq", [Variable("b"), Number(3)]),
            Fact("gt", [Variable("c"), Number(0)])
        }
        
        results = matcher.match_facts_list(patterns, targets)
        assert len(results) == 1
        assert results[0].get_mapping("X") == Variable("a")
        
        # Multiple patterns
        patterns = [
            Fact("eq", [Variable("X"), Variable("Y")]),
            Fact("gt", [Variable("Y"), Number(0)])
        ]
        targets = {
            Fact("eq", [Variable("a"), Variable("b")]),
            Fact("gt", [Variable("b"), Number(0)]),
            Fact("eq", [Variable("c"), Number(5)])
        }
        
        results = matcher.match_facts_list(patterns, targets)
        assert len(results) == 1
        assert results[0].get_mapping("X") == Variable("a")
        assert results[0].get_mapping("Y") == Variable("b")


class TestRuleApplicator:
    def test_simple_rule_application(self):
        applicator = RuleApplicator()
        
        # Rule: eq(X + A, B) → eq(X, B - A)
        premise = Fact("eq", [Operation(Variable("X"), "+", Variable("A")), Variable("B")])
        conclusion = Fact("eq", [Variable("X"), Operation(Variable("B"), "-", Variable("A"))])
        rule = Rule([premise], conclusion, "subtraction")
        
        # Available facts
        available_facts = {
            Fact("eq", [Operation(Variable("x"), "+", Number(3)), Number(7)]),
            Fact("gt", [Variable("y"), Number(0)])
        }
        
        # Apply rule
        new_facts = applicator.apply_rule(rule, available_facts)
        
        assert len(new_facts) == 1
        expected = Fact("eq", [Variable("x"), Operation(Number(7), "-", Number(3))])
        assert new_facts[0] == expected
    
    def test_multiple_premises_rule(self):
        applicator = RuleApplicator()
        
        # Rule: eq(X, Y) ∧ eq(Y, Z) → eq(X, Z)
        premise1 = Fact("eq", [Variable("X"), Variable("Y")])
        premise2 = Fact("eq", [Variable("Y"), Variable("Z")])
        conclusion = Fact("eq", [Variable("X"), Variable("Z")])
        rule = Rule([premise1, premise2], conclusion, "transitivity")
        
        # Available facts
        available_facts = {
            Fact("eq", [Variable("a"), Variable("b")]),
            Fact("eq", [Variable("b"), Variable("c")]),
            Fact("gt", [Variable("d"), Number(0)])
        }
        
        # Apply rule
        new_facts = applicator.apply_rule(rule, available_facts)
        
        assert len(new_facts) == 1
        expected = Fact("eq", [Variable("a"), Variable("c")])
        assert new_facts[0] == expected
    
    def test_no_applicable_rule(self):
        applicator = RuleApplicator()
        
        # Rule: eq(X, Y) → gt(X, 0)
        premise = Fact("eq", [Variable("X"), Variable("Y")])
        conclusion = Fact("gt", [Variable("X"), Number(0)])
        rule = Rule([premise], conclusion)
        
        # Available facts don't match premise
        available_facts = {
            Fact("gt", [Variable("a"), Number(5)]),
            Fact("odd", [Variable("b")])
        }
        
        # Apply rule
        new_facts = applicator.apply_rule(rule, available_facts)
        assert len(new_facts) == 0
        
        # Check can_apply_rule
        assert applicator.can_apply_rule(rule, available_facts) == False
    
    def test_avoid_duplicate_facts(self):
        applicator = RuleApplicator()
        
        # Rule: gt(X, Y) → gt(X, Y)  (identity rule for testing)
        premise = Fact("gt", [Variable("X"), Variable("Y")])
        conclusion = Fact("gt", [Variable("X"), Variable("Y")])
        rule = Rule([premise], conclusion)
        
        # Available facts
        available_facts = {
            Fact("gt", [Variable("a"), Variable("b")])
        }
        
        # Apply rule - should not generate duplicate
        new_facts = applicator.apply_rule(rule, available_facts)
        assert len(new_facts) == 0  # No new facts since conclusion already exists


if __name__ == "__main__":
    pytest.main([__file__])