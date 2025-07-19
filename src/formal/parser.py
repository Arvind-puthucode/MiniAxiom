"""
Mathematical expression and predicate parser with SymPy integration.

This module provides functionality to parse string expressions into our
internal representation and convert between string and formal representations.
"""
import re
from typing import List
import sympy as sp
from fractions import Fraction

from .expressions import Expression, Number, Variable, Operation, Fact, Rule


class ExpressionParser:
    """Parser for converting string expressions to internal Expression objects."""
    
    def __init__(self):
        # Mapping from string operators to our internal representation
        self.operator_mapping = {
            '+': '+',
            '-': '-', 
            '*': '*',
            '/': '/',
            '^': '^',
            '**': '^'  # Convert ** to ^ for consistency
        }
    
    def parse_expression(self, expr_str: str) -> Expression:
        """
        Parse a string expression into an Expression object.
        
        Examples:
            "5" -> Number(5)
            "x" -> Variable("x")
            "x + 3" -> Operation(Variable("x"), "+", Number(3))
            "2 * (x - 1)" -> Operation(Number(2), "*", Operation(Variable("x"), "-", Number(1)))
        """
        try:
            # Clean the input string
            expr_str = expr_str.strip()
            if not expr_str:
                raise ValueError("Empty expression")
            
            # Use SymPy to parse, but prevent automatic simplification
            sympy_expr = sp.sympify(expr_str, evaluate=False)
            
            # Convert SymPy expression to our internal representation
            return self._sympy_to_expression(sympy_expr)
            
        except Exception as e:
            raise ValueError(f"Failed to parse expression '{expr_str}': {str(e)}")
    
    def _sympy_to_expression(self, sympy_expr) -> Expression:
        """Convert a SymPy expression to our Expression representation."""
        
        if sympy_expr.is_Number:
            # Handle numbers (integers, rationals, floats)
            if sympy_expr.is_Integer:
                return Number(int(sympy_expr))
            elif sympy_expr.is_Rational:
                return Number(Fraction(int(sympy_expr.p), int(sympy_expr.q)))
            else:
                # Float - convert to fraction
                return Number(float(sympy_expr))
        
        elif sympy_expr.is_Symbol:
            # Handle variables
            return Variable(str(sympy_expr))
        
        elif sympy_expr.is_Add:
            # Handle addition: a + b + c -> ((a + b) + c)
            args = list(sympy_expr.args)
            if len(args) == 2:
                # Check if this is actually subtraction (a + (-1 * b))
                left_arg, right_arg = args
                if (hasattr(right_arg, 'is_Mul') and right_arg.is_Mul and 
                    len(right_arg.args) == 2 and right_arg.args[0] == -1):
                    # This is subtraction: a - b represented as a + (-1 * b)
                    return Operation(
                        self._sympy_to_expression(left_arg),
                        "-",
                        self._sympy_to_expression(right_arg.args[1])  # Extract b from (-1 * b)
                    )
                else:
                    # Regular addition
                    return Operation(
                        self._sympy_to_expression(left_arg),
                        "+", 
                        self._sympy_to_expression(right_arg)
                    )
            else:
                # Multiple terms - fold left
                result = self._sympy_to_expression(args[0])
                for arg in args[1:]:
                    if hasattr(arg, 'is_negative') and arg.is_negative:
                        result = Operation(result, "-", self._sympy_to_expression(-arg))
                    else:
                        result = Operation(result, "+", self._sympy_to_expression(arg))
                return result
        
        elif sympy_expr.is_Mul:
            # Handle multiplication: a * b * c -> ((a * b) * c)
            # Also handle division: a / b represented as a * (1/b)
            args = list(sympy_expr.args)
            if len(args) == 2:
                left_arg, right_arg = args
                # Check if this is division (a * (b^(-1)))
                if (hasattr(right_arg, 'is_Pow') and right_arg.is_Pow and 
                    len(right_arg.args) == 2 and right_arg.args[1] == -1):
                    # This is division: a / b represented as a * (b^(-1))
                    return Operation(
                        self._sympy_to_expression(left_arg),
                        "/",
                        self._sympy_to_expression(right_arg.args[0])  # Extract base from b^(-1)
                    )
                else:
                    # Regular multiplication
                    return Operation(
                        self._sympy_to_expression(left_arg),
                        "*", 
                        self._sympy_to_expression(right_arg)
                    )
            else:
                # Multiple factors - fold left
                result = self._sympy_to_expression(args[0])
                for arg in args[1:]:
                    result = Operation(result, "*", self._sympy_to_expression(arg))
                return result
        
        elif sympy_expr.is_Pow:
            # Handle exponentiation: a^b
            base, exp = sympy_expr.args
            return Operation(
                self._sympy_to_expression(base), 
                "^", 
                self._sympy_to_expression(exp)
            )
        
        elif hasattr(sympy_expr, 'args') and len(sympy_expr.args) == 2:
            # Handle binary operations
            left, right = sympy_expr.args
            
            if isinstance(sympy_expr, sp.Add):
                op = "+"
            elif isinstance(sympy_expr, sp.Mul):
                op = "*"
            elif isinstance(sympy_expr, sp.Pow):
                op = "^"
            elif str(type(sympy_expr)).find('Sub') != -1:
                op = "-"
            elif str(type(sympy_expr)).find('Div') != -1:
                op = "/"
            else:
                # Handle SymPy's various operation types
                class_name = sympy_expr.__class__.__name__
                if 'Add' in class_name:
                    op = "+"
                elif 'Mul' in class_name:
                    op = "*" 
                elif 'Pow' in class_name:
                    op = "^"
                else:
                    raise ValueError(f"Unsupported binary operation: {type(sympy_expr)}")
            
            return Operation(
                self._sympy_to_expression(left),
                op,
                self._sympy_to_expression(right)
            )
        
        else:
            raise ValueError(f"Unsupported SymPy expression type: {type(sympy_expr)}")


class PredicateParser:
    """Parser for converting string predicates to Fact objects."""
    
    def __init__(self):
        self.expression_parser = ExpressionParser()
        
        # Valid predicate patterns
        self.predicate_pattern = re.compile(r'^(\w+)\((.*)\)$')
    
    def parse_fact(self, fact_str: str) -> Fact:
        """
        Parse a string predicate into a Fact object.
        
        Examples:
            "eq(x, 5)" -> Fact("eq", [Variable("x"), Number(5)])
            "gt(a, b)" -> Fact("gt", [Variable("a"), Variable("b")])
            "even(n)" -> Fact("even", [Variable("n")])
        """
        try:
            fact_str = fact_str.strip()
            
            # Parse predicate pattern: predicate(arg1, arg2, ...)
            match = self.predicate_pattern.match(fact_str)
            if not match:
                raise ValueError(f"Invalid predicate format: {fact_str}")
            
            predicate = match.group(1)
            args_str = match.group(2).strip()
            
            # Parse arguments
            if not args_str:
                arguments = []
            else:
                # Split arguments by comma, respecting parentheses
                arg_strings = self._split_arguments(args_str)
                arguments = [
                    self.expression_parser.parse_expression(arg.strip()) 
                    for arg in arg_strings
                ]
            
            return Fact(predicate, arguments)
            
        except Exception as e:
            raise ValueError(f"Failed to parse fact '{fact_str}': {str(e)}")
    
    def _split_arguments(self, args_str: str) -> List[str]:
        """Split argument string by commas, respecting nested parentheses."""
        if not args_str:
            return []
        
        arguments = []
        current_arg = ""
        paren_level = 0
        
        for char in args_str:
            if char == ',' and paren_level == 0:
                arguments.append(current_arg.strip())
                current_arg = ""
            else:
                if char == '(':
                    paren_level += 1
                elif char == ')':
                    paren_level -= 1
                current_arg += char
        
        # Add the last argument
        if current_arg.strip():
            arguments.append(current_arg.strip())
        
        return arguments


class RuleParser:
    """Parser for converting string rules to Rule objects."""
    
    def __init__(self):
        self.predicate_parser = PredicateParser()
        
        # Rule pattern: premise1 ∧ premise2 → conclusion
        self.rule_pattern = re.compile(r'^(.+?)\s*→\s*(.+)$')
        self.premise_separator = re.compile(r'\s*∧\s*')
    
    def parse_rule(self, rule_str: str, name: str = "") -> Rule:
        """
        Parse a string rule into a Rule object.
        
        Examples:
            "eq(X + A, B) → eq(X, B - A)" 
            "eq(X, Y) ∧ eq(Y, Z) → eq(X, Z)"
        """
        try:
            rule_str = rule_str.strip()
            
            # Parse rule pattern
            match = self.rule_pattern.match(rule_str)
            if not match:
                raise ValueError(f"Invalid rule format: {rule_str}")
            
            premises_str = match.group(1).strip()
            conclusion_str = match.group(2).strip()
            
            # Parse premises (split by ∧)
            if premises_str:
                premise_strings = self.premise_separator.split(premises_str)
                premises = [
                    self.predicate_parser.parse_fact(p.strip()) 
                    for p in premise_strings
                ]
            else:
                premises = []
            
            # Parse conclusion
            conclusion = self.predicate_parser.parse_fact(conclusion_str)
            
            return Rule(premises, conclusion, name)
            
        except Exception as e:
            raise ValueError(f"Failed to parse rule '{rule_str}': {str(e)}")


class MathParser:
    """Main parser interface combining all parsing functionality."""
    
    def __init__(self):
        self.expression_parser = ExpressionParser()
        self.predicate_parser = PredicateParser()
        self.rule_parser = RuleParser()
    
    def parse_expression(self, expr_str: str) -> Expression:
        """Parse string expression to Expression object."""
        return self.expression_parser.parse_expression(expr_str)
    
    def parse_fact(self, fact_str: str) -> Fact:
        """Parse string predicate to Fact object."""
        return self.predicate_parser.parse_fact(fact_str)
    
    def parse_rule(self, rule_str: str, name: str = "") -> Rule:
        """Parse string rule to Rule object."""
        return self.rule_parser.parse_rule(rule_str, name)
    
    def parse_facts_list(self, facts_list: List[str]) -> List[Fact]:
        """Parse a list of fact strings."""
        return [self.parse_fact(fact_str) for fact_str in facts_list]
    
    def parse_rules_list(self, rules_list: List[str], names: List[str] = None) -> List[Rule]:
        """Parse a list of rule strings."""
        if names is None:
            names = [""] * len(rules_list)
        
        return [
            self.parse_rule(rule_str, name) 
            for rule_str, name in zip(rules_list, names)
        ]