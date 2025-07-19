"""
Test suite for mathematical rule system.
"""
import pytest
from src.reasoning.rules import MathematicalRules, RuleSystem
from src.formal.expressions import Operation


class TestMathematicalRules:
    def test_rule_initialization(self):
        rules = MathematicalRules()
        
        # Check that rules are loaded
        all_rules = rules.get_all_rules()
        assert len(all_rules) > 0
        
        # Check that rule names are available
        rule_names = rules.list_rule_names()
        assert "subtraction_property" in rule_names
        assert "equality_transitivity" in rule_names
        assert "greater_transitivity" in rule_names
    
    def test_get_rule_by_name(self):
        rules = MathematicalRules()
        
        # Get subtraction property rule
        rule = rules.get_rule("subtraction_property")
        assert rule.name == "subtraction_property"
        assert len(rule.premises) == 1
        assert rule.premises[0].predicate == "eq"
        assert rule.conclusion.predicate == "eq"
        
        # Test invalid rule name
        with pytest.raises(ValueError):
            rules.get_rule("nonexistent_rule")
    
    def test_algebraic_rules(self):
        rules = MathematicalRules()
        algebraic_rules = rules.get_rules_by_category("algebraic")
        
        assert len(algebraic_rules) > 0
        rule_names = [r.name for r in algebraic_rules]
        assert "subtraction_property" in rule_names
        assert "division_property" in rule_names
        assert "equality_transitivity" in rule_names
    
    def test_arithmetic_rules(self):
        rules = MathematicalRules()
        arithmetic_rules = rules.get_rules_by_category("arithmetic")
        
        assert len(arithmetic_rules) > 0
        rule_names = [r.name for r in arithmetic_rules]
        assert "even_multiplication" in rule_names
        assert "odd_multiplication" in rule_names
    
    def test_comparison_rules(self):
        rules = MathematicalRules()
        comparison_rules = rules.get_rules_by_category("comparison")
        
        assert len(comparison_rules) > 0
        rule_names = [r.name for r in comparison_rules]
        assert "greater_transitivity" in rule_names
        assert "equality_substitution_gt" in rule_names
    
    def test_number_theory_rules(self):
        rules = MathematicalRules()
        nt_rules = rules.get_rules_by_category("number_theory")
        
        assert len(nt_rules) > 0
        rule_names = [r.name for r in nt_rules]
        assert "divisibility_transitivity" in rule_names
    
    def test_invalid_category(self):
        rules = MathematicalRules()
        
        with pytest.raises(ValueError):
            rules.get_rules_by_category("invalid_category")


class TestRuleSystem:
    def test_initialization(self):
        system = RuleSystem()
        
        # All rules should be active by default
        active_rules = system.get_active_rules()
        assert len(active_rules) > 0
        
        # Check that specific rules are active
        assert system.is_rule_active("subtraction_property")
        assert system.is_rule_active("equality_transitivity")
    
    def test_enable_disable_rule(self):
        system = RuleSystem()
        
        # Disable a rule
        system.disable_rule("subtraction_property")
        assert not system.is_rule_active("subtraction_property")
        
        # Enable it back
        system.enable_rule("subtraction_property")
        assert system.is_rule_active("subtraction_property")
        
        # Test invalid rule name
        with pytest.raises(ValueError):
            system.enable_rule("nonexistent_rule")
    
    def test_category_operations(self):
        system = RuleSystem()
        
        # Disable algebraic category
        system.disable_category("algebraic")
        assert not system.is_rule_active("subtraction_property")
        assert not system.is_rule_active("equality_transitivity")
        
        # Other categories should still be active
        assert system.is_rule_active("greater_transitivity")
        
        # Enable algebraic category back
        system.enable_category("algebraic")
        assert system.is_rule_active("subtraction_property")
        assert system.is_rule_active("equality_transitivity")
    
    def test_get_rule_info(self):
        system = RuleSystem()
        
        info = system.get_rule_info("subtraction_property")
        assert info["name"] == "subtraction_property"
        assert info["active"] == True
        assert len(info["premises"]) == 1
        assert info["conclusion"] is not None
        
        # Test invalid rule name
        with pytest.raises(ValueError):
            system.get_rule_info("nonexistent_rule")
    
    def test_active_rules_filtering(self):
        system = RuleSystem()
        
        # Get initial count
        initial_count = len(system.get_active_rules())
        
        # Disable some rules
        system.disable_rule("subtraction_property")
        system.disable_rule("equality_transitivity")
        
        # Count should decrease
        new_count = len(system.get_active_rules())
        assert new_count == initial_count - 2
        
        # Disabled rules should not be in active list
        active_names = [r.name for r in system.get_active_rules()]
        assert "subtraction_property" not in active_names
        assert "equality_transitivity" not in active_names


class TestRuleContent:
    """Test the actual mathematical content of rules."""
    
    def test_subtraction_property_structure(self):
        rules = MathematicalRules()
        rule = rules.get_rule("subtraction_property")
        
        # Should have one premise: eq(X + A, B)
        assert len(rule.premises) == 1
        premise = rule.premises[0]
        assert premise.predicate == "eq"
        assert len(premise.arguments) == 2
        
        # First argument should be X + A
        first_arg = premise.arguments[0]
        assert isinstance(first_arg, Operation)
        assert first_arg.operator == "+"
        
        # Conclusion should be eq(X, B - A)
        conclusion = rule.conclusion
        assert conclusion.predicate == "eq"
        assert len(conclusion.arguments) == 2
        
        # Second argument should be B - A
        second_arg = conclusion.arguments[1]
        assert isinstance(second_arg, Operation)
        assert second_arg.operator == "-"
    
    def test_transitivity_rule_structure(self):
        rules = MathematicalRules()
        rule = rules.get_rule("equality_transitivity")
        
        # Should have two premises
        assert len(rule.premises) == 2
        
        # Both premises should be eq predicates
        for premise in rule.premises:
            assert premise.predicate == "eq"
            assert len(premise.arguments) == 2
        
        # Conclusion should be eq predicate
        assert rule.conclusion.predicate == "eq"
        assert len(rule.conclusion.arguments) == 2
    
    def test_greater_transitivity_structure(self):
        rules = MathematicalRules()
        rule = rules.get_rule("greater_transitivity")
        
        # Should have two premises: gt(X, Y) and gt(Y, Z)
        assert len(rule.premises) == 2
        for premise in rule.premises:
            assert premise.predicate == "gt"
            assert len(premise.arguments) == 2
        
        # Conclusion should be gt(X, Z)
        conclusion = rule.conclusion
        assert conclusion.predicate == "gt"
        assert len(conclusion.arguments) == 2


if __name__ == "__main__":
    pytest.main([__file__])