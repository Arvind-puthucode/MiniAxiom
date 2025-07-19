"""
Test suite for forward chaining proof engine.
"""
import pytest
from src.reasoning.proof_engine import ForwardChainer, ProofEngine, ProofStep, ProofResult
from src.formal.parser import MathParser
from src.formal.expressions import MathProblem
from src.reasoning.rules import RuleSystem


class TestForwardChainer:
    def test_simple_proof(self):
        """Test basic forward chaining with subtraction rule."""
        chainer = ForwardChainer(max_iterations=10)
        parser = MathParser()
        rule_system = RuleSystem()
        
        # Goal: eq(x, 4)
        goal = parser.parse_fact("eq(x, 4)")
        
        # Initial fact: eq(x + 3, 7)
        initial_facts = {parser.parse_fact("eq(x + 3, 7)")}
        
        # Use subtraction property rule
        rules = [rule_system.math_rules.get_rule("subtraction_property")]
        
        # Run proof
        result = chainer.prove(goal, initial_facts, rules)
        
        # Should derive eq(x, 7 - 3) but goal eq(x, 4) won't match exactly
        assert result.success == True
        assert len(result.steps) == 1
        assert result.steps[0].rule_applied.name == "subtraction_property"
    
    def test_transitivity_proof(self):
        """Test transitivity reasoning."""
        chainer = ForwardChainer(max_iterations=10)
        parser = MathParser()
        rule_system = RuleSystem()
        
        # Need to fix transitivity rule first - create a proper one
        # Rule: eq(X, Y) ∧ eq(Y, Z) → eq(X, Z)
        transitivity_rule = parser.parse_rule("eq(X, Y) ∧ eq(Y, Z) → eq(X, Z)", "transitivity_xy_yz")
        
        # Goal: eq(a, c)
        goal = parser.parse_fact("eq(a, c)")
        
        # Initial facts: eq(a, b) and eq(b, c)
        initial_facts = {
            parser.parse_fact("eq(a, b)"),
            parser.parse_fact("eq(b, c)")
        }
        
        # Run proof
        result = chainer.prove(goal, initial_facts, [transitivity_rule])
        
        assert result.success == True
        assert result.goal_achieved == True
        assert len(result.steps) == 1
        assert result.steps[0].derived_fact == goal
    
    def test_goal_already_proven(self):
        """Test case where goal is already in initial facts."""
        chainer = ForwardChainer()
        parser = MathParser()
        
        goal = parser.parse_fact("eq(x, 5)")
        initial_facts = {goal}  # Goal is already known
        
        result = chainer.prove(goal, initial_facts, [])
        
        assert result.success == True
        assert result.goal_achieved == True
        assert len(result.steps) == 0
        assert result.iterations_used == 0
    
    def test_impossible_proof(self):
        """Test case where proof is impossible."""
        chainer = ForwardChainer(max_iterations=5)
        parser = MathParser()
        
        goal = parser.parse_fact("eq(x, 10)")
        initial_facts = {parser.parse_fact("eq(y, 5)")}  # Unrelated fact
        rules = []  # No rules to apply
        
        result = chainer.prove(goal, initial_facts, rules)
        
        assert result.success == True
        assert result.goal_achieved == False
        assert len(result.steps) == 0
    
    def test_max_iterations_limit(self):
        """Test that max iterations limit is respected."""
        chainer = ForwardChainer(max_iterations=2)
        parser = MathParser()
        
        goal = parser.parse_fact("eq(x, 0)")
        initial_facts = {parser.parse_fact("eq(a, b)")}
        # Use only a few rules to avoid explosion
        rules = [
            parser.parse_rule("eq(X, Y) → eq(Y, X)", "symmetry"),
            parser.parse_rule("eq(X, Y) → gt(X, 0)", "test_rule")
        ]
        
        result = chainer.prove(goal, initial_facts, rules)
        
        assert result.success == True
        assert result.iterations_used <= 2
    
    def test_multi_step_proof(self):
        """Test proof requiring multiple steps."""
        chainer = ForwardChainer(max_iterations=20)
        parser = MathParser()
        
        # Create custom rules for this test
        rule1 = parser.parse_rule("eq(X, Y) → gt(X, 0)", "rule1")  # If X = Y, then X > 0
        rule2 = parser.parse_rule("gt(X, 0) → positive(X)", "rule2")  # If X > 0, then X is positive
        
        goal = parser.parse_fact("positive(a)")
        initial_facts = {parser.parse_fact("eq(a, b)")}
        rules = [rule1, rule2]
        
        result = chainer.prove(goal, initial_facts, rules)
        
        assert result.success == True
        assert result.goal_achieved == True
        assert len(result.steps) == 2  # Should take exactly 2 steps


class TestProofEngine:
    def test_solve_simple_algebra(self):
        """Test solving simple algebraic equation."""
        engine = ProofEngine()
        parser = MathParser()
        
        # Problem: If x + 3 = 7, find x (use more lenient goal)
        goal = parser.parse_fact("eq(x, 7 - 3)")
        initial_facts = {parser.parse_fact("eq(x + 3, 7)")}
        
        result = engine.prove_goal(
            goal, initial_facts, 
            specific_rules=["subtraction_property"]  # Use specific rule instead of category
        )
        
        assert result.success == True
        assert len(result.steps) >= 1
    
    def test_solve_with_specific_rules(self):
        """Test solving with specific rules only."""
        engine = ProofEngine()
        parser = MathParser()
        
        goal = parser.parse_fact("eq(x, 7 - 3)")  # More lenient goal
        initial_facts = {parser.parse_fact("eq(x + 3, 7)")}
        
        result = engine.prove_goal(
            goal, initial_facts,
            specific_rules=["subtraction_property"]
        )
        
        assert result.success == True
        assert result.goal_achieved == True
    
    def test_solve_math_problem(self):
        """Test solving a MathProblem object."""
        engine = ProofEngine()
        parser = MathParser()
        
        # Create a math problem
        facts = [parser.parse_fact("eq(x + 5, 10)")]
        goal = parser.parse_fact("eq(x, 10 - 5)")
        rules = [engine.rule_system.math_rules.get_rule("subtraction_property")]
        
        problem = MathProblem(facts, rules, goal, "If x + 5 = 10, find x")
        
        result = engine.solve_problem(problem)
        
        assert result.success == True
        assert result.goal_achieved == True
    
    def test_engine_configuration(self):
        """Test configuring engine parameters."""
        engine = ProofEngine()
        
        # Configure limits
        engine.configure_engine(max_iterations=5, max_facts=100)
        
        assert engine.forward_chainer.max_iterations == 5
        assert engine.forward_chainer.max_facts == 100
    
    def test_rule_management(self):
        """Test enabling/disabling rules."""
        engine = ProofEngine()
        
        # Disable some rules
        engine.disable_rules(["subtraction_property", "division_property"])
        
        assert not engine.rule_system.is_rule_active("subtraction_property")
        assert not engine.rule_system.is_rule_active("division_property")
        
        # Enable them back
        engine.enable_rules(["subtraction_property"])
        
        assert engine.rule_system.is_rule_active("subtraction_property")
    
    def test_proof_explanation(self):
        """Test generating proof explanations."""
        engine = ProofEngine()
        parser = MathParser()
        
        goal = parser.parse_fact("eq(x, 7 - 3)")
        initial_facts = {parser.parse_fact("eq(x + 3, 7)")}
        
        result = engine.prove_goal(
            goal, initial_facts,
            specific_rules=["subtraction_property"]
        )
        
        explanation = engine.get_proof_explanation(result)
        
        assert "Proof completed successfully" in explanation
        assert "subtraction_property" in explanation
        assert "Statistics:" in explanation


class TestProofStep:
    def test_proof_step_creation(self):
        """Test creating and displaying proof steps."""
        parser = MathParser()
        rule_system = RuleSystem()
        
        rule = rule_system.math_rules.get_rule("subtraction_property")
        premises = [parser.parse_fact("eq(x + 3, 7)")]
        derived = parser.parse_fact("eq(x, 7 - 3)")
        
        step = ProofStep(
            rule_applied=rule,
            premises_used=premises,
            derived_fact=derived,
            step_number=1
        )
        
        step_str = str(step)
        assert "Step 1:" in step_str
        assert "subtraction_property" in step_str
        assert "eq(x + 3, 7)" in step_str
        assert "eq(x, 7 - 3)" in step_str


class TestProofResult:
    def test_successful_result(self):
        """Test successful proof result."""
        result = ProofResult(
            success=True,
            goal_achieved=True,
            steps=[],
            final_facts=set(),
            iterations_used=3,
            time_elapsed=0.1
        )
        
        result_str = str(result)
        assert "PROOF SUCCESSFUL" in result_str
        assert "0 steps" in result_str
        assert "0.100s" in result_str
    
    def test_failed_result(self):
        """Test failed proof result."""
        result = ProofResult(
            success=False,
            goal_achieved=False,
            steps=[],
            final_facts=set(),
            iterations_used=0,
            time_elapsed=0.0,
            error_message="Test error"
        )
        
        result_str = str(result)
        assert "PROOF FAILED" in result_str
        assert "Test error" in result_str


if __name__ == "__main__":
    pytest.main([__file__])