"""
Core mathematical expression data structures for the MathGraph system.

This module defines the fundamental building blocks for representing
mathematical expressions in our formal reasoning system.
"""
from abc import ABC, abstractmethod
from typing import Union, List, Dict, Any
from fractions import Fraction
import sympy as sp


class Expression(ABC):
    """Abstract base class for all mathematical expressions."""
    
    @abstractmethod
    def __eq__(self, other) -> bool:
        pass
    
    @abstractmethod
    def __hash__(self) -> int:
        pass
    
    @abstractmethod
    def __str__(self) -> str:
        pass
    
    @abstractmethod
    def to_sympy(self) -> sp.Expr:
        """Convert to SymPy expression for processing."""
        pass


class Number(Expression):
    """Represents a numeric value (integer or rational)."""
    
    def __init__(self, value: Union[int, float, Fraction]):
        if isinstance(value, float):
            self.value = Fraction(value).limit_denominator()
        elif isinstance(value, (int, Fraction)):
            self.value = value
        else:
            raise ValueError(f"Invalid number type: {type(value)}")
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Number) and self.value == other.value
    
    def __hash__(self) -> int:
        return hash(('Number', self.value))
    
    def __str__(self) -> str:
        if isinstance(self.value, Fraction) and self.value.denominator != 1:
            return f"{self.value.numerator}/{self.value.denominator}"
        return str(self.value)
    
    def to_sympy(self) -> sp.Expr:
        return sp.Rational(self.value)


class Variable(Expression):
    """Represents a mathematical variable."""
    
    def __init__(self, name: str):
        if not name or not isinstance(name, str):
            raise ValueError("Variable name must be a non-empty string")
        if not name.replace('_', '').isalnum() or name[0].isdigit():
            raise ValueError("Variable name must be alphanumeric and not start with a digit")
        self.name = name
    
    def __eq__(self, other) -> bool:
        return isinstance(other, Variable) and self.name == other.name
    
    def __hash__(self) -> int:
        return hash(('Variable', self.name))
    
    def __str__(self) -> str:
        return self.name
    
    def to_sympy(self) -> sp.Expr:
        return sp.Symbol(self.name)


class Operation(Expression):
    """Represents a mathematical operation between two expressions."""
    
    VALID_OPERATORS = {'+', '-', '*', '/', '^', '**'}
    
    def __init__(self, left: Expression, operator: str, right: Expression):
        if operator not in self.VALID_OPERATORS:
            raise ValueError(f"Invalid operator: {operator}. Must be one of {self.VALID_OPERATORS}")
        if not isinstance(left, Expression) or not isinstance(right, Expression):
            raise ValueError("Operands must be Expression instances")
        
        self.left = left
        self.operator = operator
        self.right = right
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, Operation) and 
                self.left == other.left and 
                self.operator == other.operator and 
                self.right == other.right)
    
    def __hash__(self) -> int:
        return hash(('Operation', self.left, self.operator, self.right))
    
    def __str__(self) -> str:
        # Add parentheses for clarity
        left_str = str(self.left)
        right_str = str(self.right)
        
        if isinstance(self.left, Operation):
            left_str = f"({left_str})"
        if isinstance(self.right, Operation):
            right_str = f"({right_str})"
            
        # Handle power operator display
        if self.operator in ['^', '**']:
            return f"{left_str}^{right_str}"
        
        return f"{left_str} {self.operator} {right_str}"
    
    def to_sympy(self) -> sp.Expr:
        left_sympy = self.left.to_sympy()
        right_sympy = self.right.to_sympy()
        
        if self.operator == '+':
            return left_sympy + right_sympy
        elif self.operator == '-':
            return left_sympy - right_sympy
        elif self.operator == '*':
            return left_sympy * right_sympy
        elif self.operator == '/':
            return left_sympy / right_sympy
        elif self.operator in ['^', '**']:
            return left_sympy ** right_sympy
        else:
            raise ValueError(f"Unsupported operator: {self.operator}")


class Fact:
    """Represents a logical statement about mathematical objects."""
    
    VALID_PREDICATES = {
        'eq', 'gt', 'lt', 'gte', 'lte',  # Equality and comparison
        'even', 'odd', 'prime', 'positive', 'negative',  # Number properties
        'divides', 'multiple'  # Arithmetic relations
    }
    
    def __init__(self, predicate: str, arguments: List[Expression]):
        if predicate not in self.VALID_PREDICATES:
            raise ValueError(f"Invalid predicate: {predicate}. Must be one of {self.VALID_PREDICATES}")
        if not isinstance(arguments, list) or not all(isinstance(arg, Expression) for arg in arguments):
            raise ValueError("Arguments must be a list of Expression instances")
        
        # Validate argument count for each predicate
        expected_args = self._get_expected_arg_count(predicate)
        if len(arguments) != expected_args:
            raise ValueError(f"Predicate '{predicate}' expects {expected_args} arguments, got {len(arguments)}")
        
        self.predicate = predicate
        self.arguments = arguments
    
    def _get_expected_arg_count(self, predicate: str) -> int:
        """Get expected number of arguments for each predicate."""
        if predicate in ['eq', 'gt', 'lt', 'gte', 'lte', 'divides', 'multiple']:
            return 2
        elif predicate in ['even', 'odd', 'prime', 'positive', 'negative']:
            return 1
        else:
            raise ValueError(f"Unknown predicate: {predicate}")
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, Fact) and 
                self.predicate == other.predicate and 
                self.arguments == other.arguments)
    
    def __hash__(self) -> int:
        return hash(('Fact', self.predicate, tuple(self.arguments)))
    
    def __str__(self) -> str:
        args_str = ', '.join(str(arg) for arg in self.arguments)
        return f"{self.predicate}({args_str})"
    
    def __repr__(self) -> str:
        return self.__str__()


class Rule:
    """Represents an inference rule in the form: premises → conclusion."""
    
    def __init__(self, premises: List[Fact], conclusion: Fact, name: str = ""):
        if not isinstance(premises, list) or not all(isinstance(p, Fact) for p in premises):
            raise ValueError("Premises must be a list of Fact instances")
        if not isinstance(conclusion, Fact):
            raise ValueError("Conclusion must be a Fact instance")
        
        self.premises = premises
        self.conclusion = conclusion
        self.name = name or f"rule_{id(self)}"
    
    def __eq__(self, other) -> bool:
        return (isinstance(other, Rule) and 
                self.premises == other.premises and 
                self.conclusion == other.conclusion)
    
    def __hash__(self) -> int:
        return hash(('Rule', tuple(self.premises), self.conclusion))
    
    def __str__(self) -> str:
        if not self.premises:
            return f"{self.conclusion}"
        
        premises_str = ' ∧ '.join(str(p) for p in self.premises)
        return f"{premises_str} → {self.conclusion}"
    
    def __repr__(self) -> str:
        return f"Rule(name='{self.name}', rule='{self.__str__()}')"


class MathProblem:
    """Container for a complete mathematical problem specification."""
    
    def __init__(self, facts: List[Fact], rules: List[Rule], goal: Fact, 
                 original_text: str = "", metadata: Dict[str, Any] = None):
        if not isinstance(facts, list) or not all(isinstance(f, Fact) for f in facts):
            raise ValueError("Facts must be a list of Fact instances")
        if not isinstance(rules, list) or not all(isinstance(r, Rule) for r in rules):
            raise ValueError("Rules must be a list of Rule instances")
        if not isinstance(goal, Fact):
            raise ValueError("Goal must be a Fact instance")
        
        self.facts = facts
        self.rules = rules
        self.goal = goal
        self.original_text = original_text
        self.metadata = metadata or {}
    
    def __str__(self) -> str:
        facts_str = '\n  '.join(str(f) for f in self.facts)
        rules_str = '\n  '.join(str(r) for r in self.rules)
        return (f"MathProblem(\n"
                f"  Facts: {facts_str}\n"
                f"  Rules: {rules_str}\n"
                f"  Goal: {self.goal}\n"
                f")")
    
    def validate(self) -> bool:
        """Basic validation of problem consistency."""
        try:
            # Check that all facts are well-formed
            for fact in self.facts:
                if not fact.predicate or not fact.arguments:
                    return False
            
            # Check that goal is well-formed
            if not self.goal.predicate or not self.goal.arguments:
                return False
            
            # Check that rules are well-formed
            for rule in self.rules:
                if not rule.premises or not rule.conclusion:
                    return False
            
            return True
        except Exception:
            return False