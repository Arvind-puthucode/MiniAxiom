"""
LLM-based problem extraction from natural language.

This module uses Azure OpenAI to convert natural language mathematical problems
into formal representations that can be processed by the reasoning engine.
"""
from typing import Dict, List, Optional, Any
from ..formal.expressions import MathProblem
from ..formal.parser import MathParser
from .llm_client import AzureOpenAIClient


class ProblemExtractor:
    """Extract formal mathematical problems from natural language."""
    
    def __init__(self):
        self.llm_client = AzureOpenAIClient()
        self.parser = MathParser()
        
        # Template for extraction prompts
        self.extraction_template = """
You are a mathematical logic expert. Convert this natural language problem to formal logic.

Problem: {problem_text}

STRICT REQUIREMENTS:
1. Use ONLY these predicates: eq, gt, lt, gte, lte, even, odd, prime, positive, negative, divides, multiple
2. Variables must be single letters: x, y, z, n, a, b, c (use lowercase for concrete variables, uppercase for pattern variables)
3. Numbers must be integers or simple arithmetic expressions
4. No undefined functions or predicates
5. Facts are concrete statements about the problem
6. Rules are inference patterns that can be applied
7. Goal is the single statement we want to prove

OUTPUT FORMAT (valid JSON):
{{
  "facts": ["eq(x + 3, 7)"],
  "rules": ["eq(X + A, B) → eq(X, B - A)"],
  "goal": "eq(x, 4)",
  "problem_type": "algebraic_equation",
  "confidence": 0.9
}}

EXAMPLES:

Problem: "If x + 3 = 7, find x"
{{
  "facts": ["eq(x + 3, 7)"],
  "rules": ["eq(X + A, B) → eq(X, B - A)"],
  "goal": "eq(x, 7 - 3)",
  "problem_type": "algebraic_equation",
  "confidence": 0.95
}}

Problem: "If n is even, prove n² is even"
{{
  "facts": ["even(n)"],
  "rules": ["even(X) → even(X * X)"],
  "goal": "even(n * n)",
  "problem_type": "number_theory",
  "confidence": 0.9
}}

Problem: "If a > b and b > c, prove a > c"
{{
  "facts": ["gt(a, b)", "gt(b, c)"],
  "rules": ["gt(X, Y) ∧ gt(Y, Z) → gt(X, Z)"],
  "goal": "gt(a, c)",
  "problem_type": "inequality",
  "confidence": 0.95
}}

Now process: {problem_text}
"""
    
    def extract(self, natural_language: str) -> MathProblem:
        """
        Extract a formal mathematical problem from natural language.
        
        Args:
            natural_language: Natural language description of the problem
            
        Returns:
            MathProblem object with extracted facts, rules, and goal
            
        Raises:
            ValueError: If extraction fails or produces invalid results
        """
        try:
            # Generate extraction prompt
            prompt = self.extraction_template.format(problem_text=natural_language)
            
            # Get JSON response from LLM
            response = self.llm_client.generate_json_completion(prompt, max_tokens=800)
            
            # Validate response structure
            self._validate_response(response)
            
            # Parse the formal representations
            facts = self._parse_facts(response["facts"])
            rules = self._parse_rules(response["rules"])
            goal = self._parse_goal(response["goal"])
            
            # Create metadata
            metadata = {
                "original_text": natural_language,
                "problem_type": response.get("problem_type", "unknown"),
                "confidence": response.get("confidence", 0.0),
                "llm_response": response
            }
            
            return MathProblem(
                facts=facts,
                rules=rules,
                goal=goal,
                original_text=natural_language,
                metadata=metadata
            )
            
        except Exception as e:
            raise ValueError(f"Failed to extract problem from '{natural_language}': {str(e)}")
    
    def _validate_response(self, response: Dict[str, Any]):
        """Validate the LLM response structure."""
        required_fields = ["facts", "rules", "goal"]
        
        for field in required_fields:
            if field not in response:
                raise ValueError(f"Missing required field: {field}")
        
        if not isinstance(response["facts"], list):
            raise ValueError("Facts must be a list")
        
        if not isinstance(response["rules"], list):
            raise ValueError("Rules must be a list")
        
        if not isinstance(response["goal"], str):
            raise ValueError("Goal must be a string")
    
    def _parse_facts(self, fact_strings: List[str]) -> List:
        """Parse fact strings into Fact objects."""
        facts = []
        for fact_str in fact_strings:
            try:
                fact = self.parser.parse_fact(fact_str)
                facts.append(fact)
            except Exception as e:
                raise ValueError(f"Failed to parse fact '{fact_str}': {str(e)}")
        return facts
    
    def _parse_rules(self, rule_strings: List[str]) -> List:
        """Parse rule strings into Rule objects."""
        rules = []
        for i, rule_str in enumerate(rule_strings):
            try:
                rule = self.parser.parse_rule(rule_str, f"extracted_rule_{i}")
                rules.append(rule)
            except Exception as e:
                # Check if this is actually a fact that was mislabeled as a rule
                if "Invalid rule format" in str(e):
                    try:
                        # Try parsing as a fact
                        fact = self.parser.parse_fact(rule_str)
                        # Convert fact to a rule: fact → fact (identity rule)
                        from ..formal.expressions import Rule
                        identity_rule = Rule([fact], fact, f"identity_rule_{i}")
                        rules.append(identity_rule)
                        continue
                    except:
                        pass  # If fact parsing also fails, fall through to original error
                
                raise ValueError(f"Failed to parse rule '{rule_str}': {str(e)}")
        return rules
    
    def _parse_goal(self, goal_string: str):
        """Parse goal string into Fact object."""
        try:
            return self.parser.parse_fact(goal_string)
        except Exception as e:
            raise ValueError(f"Failed to parse goal '{goal_string}': {str(e)}")
    
    def extract_with_fallback(self, natural_language: str, 
                            fallback_templates: Optional[Dict[str, Dict]] = None) -> MathProblem:
        """
        Extract with fallback to template-based extraction if LLM fails.
        
        Args:
            natural_language: Natural language problem
            fallback_templates: Dictionary of problem patterns and their formal representations
            
        Returns:
            MathProblem object
        """
        try:
            # Try LLM extraction first
            return self.extract(natural_language)
        except Exception as llm_error:
            # Try template-based fallback
            if fallback_templates:
                for pattern, template in fallback_templates.items():
                    if pattern.lower() in natural_language.lower():
                        return self._create_from_template(natural_language, template)
            
            # If all fails, raise the original LLM error
            raise llm_error
    
    def _create_from_template(self, natural_language: str, template: Dict) -> MathProblem:
        """Create MathProblem from a template."""
        facts = self._parse_facts(template["facts"])
        rules = self._parse_rules(template["rules"])
        goal = self._parse_goal(template["goal"])
        
        metadata = {
            "original_text": natural_language,
            "problem_type": template.get("problem_type", "template"),
            "confidence": 0.7,  # Lower confidence for template-based
            "extraction_method": "template"
        }
        
        return MathProblem(
            facts=facts,
            rules=rules,
            goal=goal,
            original_text=natural_language,
            metadata=metadata
        )


class ProblemValidator:
    """Validate extracted mathematical problems."""
    
    def __init__(self):
        pass
    
    def validate_problem(self, problem: MathProblem) -> Dict[str, Any]:
        """
        Validate a mathematical problem for consistency and solvability.
        
        Args:
            problem: MathProblem to validate
            
        Returns:
            Dictionary with validation results
        """
        results = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        # Check basic structure
        if not problem.facts:
            results["warnings"].append("No initial facts provided")
        
        if not problem.rules:
            results["warnings"].append("No inference rules provided")
        
        # Check fact consistency
        try:
            fact_predicates = [f.predicate for f in problem.facts]
            goal_predicate = problem.goal.predicate
            
            # Check if goal predicate appears in facts or could be derived
            if goal_predicate not in fact_predicates:
                rule_conclusions = [r.conclusion.predicate for r in problem.rules]
                if goal_predicate not in rule_conclusions:
                    results["warnings"].append(
                        f"Goal predicate '{goal_predicate}' may not be derivable from given facts and rules"
                    )
        except Exception as e:
            results["errors"].append(f"Error analyzing predicates: {str(e)}")
            results["is_valid"] = False
        
        # Check variable consistency
        try:
            self._check_variable_consistency(problem, results)
        except Exception as e:
            results["errors"].append(f"Error checking variables: {str(e)}")
            results["is_valid"] = False
        
        return results
    
    def _check_variable_consistency(self, problem: MathProblem, results: Dict):
        """Check that variables are used consistently."""
        # Extract all variables from facts and goal
        fact_vars = set()
        for fact in problem.facts:
            fact_vars.update(self._extract_variables_from_fact(fact))
        
        goal_vars = self._extract_variables_from_fact(problem.goal)
        
        # Check if goal variables are related to fact variables
        if goal_vars and not (goal_vars & fact_vars):
            results["warnings"].append(
                "Goal variables don't appear in facts - may be unsolvable"
            )
    
    def _extract_variables_from_fact(self, fact) -> set:
        """Extract variable names from a fact."""
        from ..formal.expressions import Variable
        
        variables = set()
        
        def extract_from_expression(expr):
            if isinstance(expr, Variable):
                variables.add(expr.name)
            elif hasattr(expr, 'left') and hasattr(expr, 'right'):
                extract_from_expression(expr.left)
                extract_from_expression(expr.right)
            elif hasattr(expr, 'arguments'):
                for arg in expr.arguments:
                    extract_from_expression(arg)
        
        for arg in fact.arguments:
            extract_from_expression(arg)
        
        return variables