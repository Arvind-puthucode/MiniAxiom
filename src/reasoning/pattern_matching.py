"""
Pattern matching system for rule applications in mathematical reasoning.

This module implements the core pattern matching algorithms needed to apply
inference rules to mathematical facts during proof search.
"""
from typing import Dict, Optional, Set, List

from ..formal.expressions import Expression, Number, Variable, Operation, Fact


class Substitution:
    """Represents variable substitutions for pattern matching."""
    
    def __init__(self, mappings: Optional[Dict[str, Expression]] = None):
        self.mappings = mappings or {}
    
    def add_mapping(self, variable: str, expression: Expression) -> bool:
        """
        Add a new variable mapping. Returns False if inconsistent with existing mappings.
        """
        if variable in self.mappings:
            return self.mappings[variable] == expression
        
        self.mappings[variable] = expression
        return True
    
    def get_mapping(self, variable: str) -> Optional[Expression]:
        """Get the expression mapped to a variable."""
        return self.mappings.get(variable)
    
    def apply_to_expression(self, expression: Expression) -> Expression:
        """Apply substitution to an expression."""
        if isinstance(expression, Variable):
            if expression.name in self.mappings:
                return self.mappings[expression.name]
            else:
                return expression
        
        elif isinstance(expression, Number):
            return expression
        
        elif isinstance(expression, Operation):
            new_left = self.apply_to_expression(expression.left)
            new_right = self.apply_to_expression(expression.right)
            return Operation(new_left, expression.operator, new_right)
        
        else:
            raise ValueError(f"Unknown expression type: {type(expression)}")
    
    def apply_to_fact(self, fact: Fact) -> Fact:
        """Apply substitution to a fact."""
        new_arguments = [self.apply_to_expression(arg) for arg in fact.arguments]
        return Fact(fact.predicate, new_arguments)
    
    def merge(self, other: 'Substitution') -> Optional['Substitution']:
        """
        Merge two substitutions. Returns None if they are inconsistent.
        """
        result = Substitution(self.mappings.copy())
        
        for var, expr in other.mappings.items():
            if not result.add_mapping(var, expr):
                return None
        
        return result
    
    def is_empty(self) -> bool:
        """Check if substitution is empty."""
        return len(self.mappings) == 0
    
    def __str__(self) -> str:
        if not self.mappings:
            return "{}"
        mappings_str = ", ".join(f"{var}: {expr}" for var, expr in self.mappings.items())
        return f"{{{mappings_str}}}"
    
    def __repr__(self) -> str:
        return f"Substitution({self.mappings})"
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Substitution) and self.mappings == other.mappings


class PatternMatcher:
    """Core pattern matching engine for mathematical expressions and facts."""
    
    def __init__(self):
        pass
    
    def match_expression(self, pattern: Expression, target: Expression) -> Optional[Substitution]:
        """
        Match a pattern expression against a target expression.
        
        Pattern variables (uppercase names) can match any expression.
        Returns substitution if match found, None otherwise.
        
        Examples:
            match_expression(Variable("X"), Number(5)) -> {X: 5}
            match_expression(Operation(Variable("X"), "+", Number(3)), 
                           Operation(Variable("y"), "+", Number(3))) -> {X: y}
        """
        return self._match_expression_recursive(pattern, target, Substitution())
    
    def _match_expression_recursive(self, pattern: Expression, target: Expression, 
                                  substitution: Substitution) -> Optional[Substitution]:
        """Recursive helper for expression matching."""
        
        if isinstance(pattern, Variable):
            # Check if this is a pattern variable (uppercase name)
            if pattern.name.isupper() or pattern.name.startswith('_'):
                # Pattern variable - can match any expression
                new_sub = substitution.mappings.copy()
                if pattern.name in new_sub:
                    # Variable already bound - check consistency
                    if new_sub[pattern.name] == target:
                        return substitution
                    else:
                        return None
                else:
                    # Bind the variable
                    new_sub[pattern.name] = target
                    return Substitution(new_sub)
            else:
                # Concrete variable - must match exactly
                if isinstance(target, Variable) and pattern.name == target.name:
                    return substitution
                else:
                    return None
        
        elif isinstance(pattern, Number):
            # Numbers must match exactly
            if isinstance(target, Number) and pattern.value == target.value:
                return substitution
            else:
                return None
        
        elif isinstance(pattern, Operation):
            # Operations must have same operator and matching operands
            if not isinstance(target, Operation):
                return None
            
            if pattern.operator != target.operator:
                return None
            
            # Match left operand
            left_match = self._match_expression_recursive(pattern.left, target.left, substitution)
            if left_match is None:
                return None
            
            # Match right operand with updated substitution
            right_match = self._match_expression_recursive(pattern.right, target.right, left_match)
            if right_match is None:
                return None
            
            return right_match
        
        else:
            raise ValueError(f"Unknown pattern type: {type(pattern)}")
    
    def match_fact(self, pattern: Fact, target: Fact) -> Optional[Substitution]:
        """
        Match a pattern fact against a target fact.
        
        Examples:
            match_fact(Fact("eq", [Variable("X"), Number(5)]), 
                      Fact("eq", [Variable("y"), Number(5)])) -> {X: y}
        """
        # Predicates must match exactly
        if pattern.predicate != target.predicate:
            return None
        
        # Number of arguments must match
        if len(pattern.arguments) != len(target.arguments):
            return None
        
        # Match all arguments
        substitution = Substitution()
        for pattern_arg, target_arg in zip(pattern.arguments, target.arguments):
            arg_match = self.match_expression(pattern_arg, target_arg)
            if arg_match is None:
                return None
            
            # Merge substitutions
            merged = substitution.merge(arg_match)
            if merged is None:
                return None
            substitution = merged
        
        return substitution
    
    def match_facts_list(self, patterns: List[Fact], targets: Set[Fact]) -> List[Substitution]:
        """
        Find all ways to match a list of pattern facts against a set of target facts.
        
        Returns list of substitutions that make all patterns match some target facts.
        """
        if not patterns:
            return [Substitution()]
        
        if len(patterns) == 1:
            # Base case: match single pattern against all targets
            matches = []
            for target in targets:
                match = self.match_fact(patterns[0], target)
                if match is not None:
                    matches.append(match)
            return matches
        
        # Recursive case: match first pattern, then remaining patterns
        first_pattern = patterns[0]
        remaining_patterns = patterns[1:]
        
        all_matches = []
        
        for target in targets:
            first_match = self.match_fact(first_pattern, target)
            if first_match is not None:
                # Found a match for first pattern, now match remaining patterns
                remaining_targets = targets - {target}  # Don't reuse the same fact
                
                remaining_matches = self.match_facts_list(remaining_patterns, remaining_targets)
                
                for remaining_match in remaining_matches:
                    # Try to merge the substitutions
                    merged = first_match.merge(remaining_match)
                    if merged is not None:
                        all_matches.append(merged)
        
        return all_matches
    
    def find_rule_matches(self, rule_premises: List[Fact], available_facts: Set[Fact]) -> List[Substitution]:
        """
        Find all ways a rule's premises can be matched against available facts.
        
        Returns list of substitutions that make all premises match available facts.
        """
        return self.match_facts_list(rule_premises, available_facts)


class RuleApplicator:
    """Applies rules to facts using pattern matching."""
    
    def __init__(self):
        self.pattern_matcher = PatternMatcher()
    
    def apply_rule(self, rule, available_facts: Set[Fact]) -> List[Fact]:
        """
        Apply a rule to available facts and return all possible new facts.
        
        Args:
            rule: Rule object with premises and conclusion
            available_facts: Set of currently known facts
            
        Returns:
            List of new facts that can be derived
        """
        new_facts = []
        
        # Find all ways the rule premises can be matched
        substitutions = self.pattern_matcher.find_rule_matches(rule.premises, available_facts)
        
        for substitution in substitutions:
            # Apply substitution to rule conclusion to get new fact
            new_fact = substitution.apply_to_fact(rule.conclusion)
            
            # Only add if it's actually new
            if new_fact not in available_facts:
                new_facts.append(new_fact)
        
        return new_facts
    
    def can_apply_rule(self, rule, available_facts: Set[Fact]) -> bool:
        """Check if a rule can be applied to the available facts."""
        substitutions = self.pattern_matcher.find_rule_matches(rule.premises, available_facts)
        return len(substitutions) > 0