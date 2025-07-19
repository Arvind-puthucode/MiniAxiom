"""
Mathematical rule system implementation.

This module defines the standard mathematical rules used for reasoning
in algebra and number theory, as specified in the SRS.
"""
from typing import List, Dict
from ..formal.expressions import Rule
from ..formal.parser import MathParser


class MathematicalRules:
    """Collection of standard mathematical inference rules."""
    
    def __init__(self):
        self.parser = MathParser()
        self._rules = {}
        self._initialize_rules()
    
    def _initialize_rules(self):
        """Initialize all mathematical rules."""
        
        # Algebraic Manipulation Rules
        self._add_algebraic_rules()
        
        # Arithmetic Property Rules  
        self._add_arithmetic_rules()
        
        # Comparison Rules
        self._add_comparison_rules()
        
        # Number Theory Rules
        self._add_number_theory_rules()
    
    def _add_algebraic_rules(self):
        """Add algebraic manipulation rules."""
        
        # R1: Subtraction property - eq(X + A, B) → eq(X, B - A)
        self._rules["subtraction_property"] = self.parser.parse_rule(
            "eq(X + A, B) → eq(X, B - A)",
            "subtraction_property"
        )
        
        # R2: Division property - eq(A * X, B) ∧ neq(A, 0) → eq(X, B / A)
        # Note: We'll implement neq as a separate check for now
        self._rules["division_property"] = self.parser.parse_rule(
            "eq(A * X, B) → eq(X, B / A)",
            "division_property"
        )
        
        # R3: Transitivity of equality - eq(X, A) ∧ eq(X, B) → eq(A, B)
        self._rules["equality_transitivity"] = self.parser.parse_rule(
            "eq(X, A) ∧ eq(X, B) → eq(A, B)",
            "equality_transitivity"
        )
        
        # Additional algebraic rules
        
        # Addition property - eq(X, A) → eq(X + B, A + B)
        self._rules["addition_property"] = self.parser.parse_rule(
            "eq(X, A) → eq(X + B, A + B)",
            "addition_property"
        )
        
        # Multiplication property - eq(X, A) → eq(X * B, A * B)
        self._rules["multiplication_property"] = self.parser.parse_rule(
            "eq(X, A) → eq(X * B, A * B)",
            "multiplication_property"
        )
        
        # Symmetric property - eq(X, Y) → eq(Y, X)
        self._rules["equality_symmetry"] = self.parser.parse_rule(
            "eq(X, Y) → eq(Y, X)",
            "equality_symmetry"
        )
        
        # Reflexive property (for completeness) - TRUE → eq(X, X)
        # We'll handle this as a special case since it doesn't need premises
    
    def _add_arithmetic_rules(self):
        """Add arithmetic property rules."""
        
        # R4: Definition of even - even(X) → eq(X, 2 * Y)
        # This rule generates existence, we'll use a simpler form
        self._rules["even_definition"] = self.parser.parse_rule(
            "eq(X, 2 * Y) → even(X)",
            "even_definition"
        )
        
        # R5: Definition of odd - odd(X) → eq(X, 2 * Y + 1)  
        self._rules["odd_definition"] = self.parser.parse_rule(
            "eq(X, 2 * Y + 1) → odd(X)",
            "odd_definition"
        )
        
        # R6: Even multiplication - even(X) → even(X * Y)
        self._rules["even_multiplication"] = self.parser.parse_rule(
            "even(X) → even(X * Y)",
            "even_multiplication"
        )
        
        # R7: Odd multiplication - odd(X) ∧ odd(Y) → odd(X * Y)
        self._rules["odd_multiplication"] = self.parser.parse_rule(
            "odd(X) ∧ odd(Y) → odd(X * Y)",
            "odd_multiplication"
        )
        
        # Additional arithmetic rules
        
        # Even + Even = Even
        self._rules["even_addition"] = self.parser.parse_rule(
            "even(X) ∧ even(Y) → even(X + Y)",
            "even_addition"
        )
        
        # Odd + Odd = Even
        self._rules["odd_addition_even"] = self.parser.parse_rule(
            "odd(X) ∧ odd(Y) → even(X + Y)",
            "odd_addition_even"
        )
        
        # Even + Odd = Odd
        self._rules["even_odd_addition"] = self.parser.parse_rule(
            "even(X) ∧ odd(Y) → odd(X + Y)",
            "even_odd_addition"
        )
        
        # Square of even is even
        self._rules["even_square"] = self.parser.parse_rule(
            "even(X) → even(X * X)",
            "even_square"
        )
        
        # Square of odd is odd
        self._rules["odd_square"] = self.parser.parse_rule(
            "odd(X) → odd(X * X)",
            "odd_square"
        )
    
    def _add_comparison_rules(self):
        """Add comparison and inequality rules."""
        
        # R8: Transitivity of > - gt(X, Y) ∧ gt(Y, Z) → gt(X, Z)
        self._rules["greater_transitivity"] = self.parser.parse_rule(
            "gt(X, Y) ∧ gt(Y, Z) → gt(X, Z)",
            "greater_transitivity"
        )
        
        # R9: Equality substitution in inequality - eq(X, Y) ∧ gt(Y, Z) → gt(X, Z)
        self._rules["equality_substitution_gt"] = self.parser.parse_rule(
            "eq(X, Y) ∧ gt(Y, Z) → gt(X, Z)",
            "equality_substitution_gt"
        )
        
        # Additional comparison rules
        
        # Transitivity of <
        self._rules["less_transitivity"] = self.parser.parse_rule(
            "lt(X, Y) ∧ lt(Y, Z) → lt(X, Z)",
            "less_transitivity"
        )
        
        # Transitivity of >=
        self._rules["gte_transitivity"] = self.parser.parse_rule(
            "gte(X, Y) ∧ gte(Y, Z) → gte(X, Z)",
            "gte_transitivity"
        )
        
        # Transitivity of <=
        self._rules["lte_transitivity"] = self.parser.parse_rule(
            "lte(X, Y) ∧ lte(Y, Z) → lte(X, Z)",
            "lte_transitivity"
        )
        
        # gt and lt relationship
        self._rules["gt_lt_relationship"] = self.parser.parse_rule(
            "gt(X, Y) → lt(Y, X)",
            "gt_lt_relationship"
        )
    
    def _add_number_theory_rules(self):
        """Add number theory and divisibility rules."""
        
        # R10: Divisibility transitivity - divides(A, B) ∧ divides(B, C) → divides(A, C)
        self._rules["divisibility_transitivity"] = self.parser.parse_rule(
            "divides(A, B) ∧ divides(B, C) → divides(A, C)",
            "divisibility_transitivity"
        )
        
        # Additional number theory rules
        
        # Every number divides itself
        # Note: This would need special handling as it's a universal rule
        
        # 1 divides everything - divides(1, X) (always true)
        # We'll handle this as a fact generator
        
        # Multiple relationship
        self._rules["multiple_divides"] = self.parser.parse_rule(
            "multiple(X, Y) → divides(Y, X)",
            "multiple_divides"
        )
        
        # Divisibility and multiplication
        self._rules["divisibility_multiplication"] = self.parser.parse_rule(
            "divides(A, B) → divides(A, B * C)",
            "divisibility_multiplication"
        )
        
        # Prime properties (simplified)
        self._rules["prime_not_even"] = self.parser.parse_rule(
            "prime(X) ∧ gt(X, 2) → odd(X)",
            "prime_not_even"
        )
    
    def get_rule(self, name: str) -> Rule:
        """Get a rule by name."""
        if name not in self._rules:
            raise ValueError(f"Unknown rule: {name}")
        return self._rules[name]
    
    def get_all_rules(self) -> List[Rule]:
        """Get all rules as a list."""
        return list(self._rules.values())
    
    def get_rules_by_category(self, category: str) -> List[Rule]:
        """Get rules by category."""
        category_mapping = {
            "algebraic": [
                "subtraction_property", "division_property", "equality_transitivity",
                "addition_property", "multiplication_property", "equality_symmetry"
            ],
            "arithmetic": [
                "even_definition", "odd_definition", "even_multiplication", "odd_multiplication",
                "even_addition", "odd_addition_even", "even_odd_addition", "even_square", "odd_square"
            ],
            "comparison": [
                "greater_transitivity", "equality_substitution_gt", "less_transitivity",
                "gte_transitivity", "lte_transitivity", "gt_lt_relationship"
            ],
            "number_theory": [
                "divisibility_transitivity", "multiple_divides", "divisibility_multiplication",
                "prime_not_even"
            ]
        }
        
        if category not in category_mapping:
            raise ValueError(f"Unknown category: {category}")
        
        return [self._rules[name] for name in category_mapping[category]]
    
    def list_rule_names(self) -> List[str]:
        """List all rule names."""
        return list(self._rules.keys())


class RuleSystem:
    """Main rule system interface."""
    
    def __init__(self):
        self.math_rules = MathematicalRules()
        self.active_rules = set(self.math_rules.list_rule_names())
    
    def enable_rule(self, rule_name: str):
        """Enable a specific rule."""
        if rule_name not in self.math_rules.list_rule_names():
            raise ValueError(f"Unknown rule: {rule_name}")
        self.active_rules.add(rule_name)
    
    def disable_rule(self, rule_name: str):
        """Disable a specific rule."""
        self.active_rules.discard(rule_name)
    
    def enable_category(self, category: str):
        """Enable all rules in a category."""
        rules = self.math_rules.get_rules_by_category(category)
        for rule in rules:
            self.active_rules.add(rule.name)
    
    def disable_category(self, category: str):
        """Disable all rules in a category."""
        rules = self.math_rules.get_rules_by_category(category)
        for rule in rules:
            self.active_rules.discard(rule.name)
    
    def get_active_rules(self) -> List[Rule]:
        """Get all currently active rules."""
        return [
            self.math_rules.get_rule(name) 
            for name in self.active_rules
        ]
    
    def is_rule_active(self, rule_name: str) -> bool:
        """Check if a rule is currently active."""
        return rule_name in self.active_rules
    
    def get_rule_info(self, rule_name: str) -> Dict:
        """Get information about a rule."""
        if rule_name not in self.math_rules.list_rule_names():
            raise ValueError(f"Unknown rule: {rule_name}")
        
        rule = self.math_rules.get_rule(rule_name)
        return {
            "name": rule.name,
            "premises": [str(p) for p in rule.premises],
            "conclusion": str(rule.conclusion),
            "active": self.is_rule_active(rule_name)
        }