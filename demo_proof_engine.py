"""
Demo script showing the forward chaining proof engine in action.
"""
from src.formal.parser import MathParser
from src.reasoning.proof_engine import ProofEngine
from src.formal.expressions import MathProblem


def demo_basic_algebra_proof():
    """Demonstrate basic algebraic proof."""
    print("=== Basic Algebraic Proof Demo ===")
    
    engine = ProofEngine()
    parser = MathParser()
    
    # Problem: If x + 3 = 7, prove x = 7 - 3
    print("\nProblem: If x + 3 = 7, prove x = 7 - 3")
    
    goal = parser.parse_fact("eq(x, 7 - 3)")
    initial_facts = {parser.parse_fact("eq(x + 3, 7)")}
    
    print(f"Goal: {goal}")
    print(f"Initial facts: {list(initial_facts)}")
    
    result = engine.prove_goal(
        goal, initial_facts,
        specific_rules=["subtraction_property"]
    )
    
    print(f"\nResult: {result}")
    if result.goal_achieved:
        print("\n" + engine.get_proof_explanation(result))
    print("-" * 50)


def demo_transitivity_proof():
    """Demonstrate transitivity proof."""
    print("=== Transitivity Proof Demo ===")
    
    engine = ProofEngine()
    parser = MathParser()
    
    # Problem: If a = b and b = c, prove a = c
    print("\nProblem: If a = b and b = c, prove a = c")
    
    # Create proper transitivity rule
    transitivity_rule = parser.parse_rule("eq(X, Y) ∧ eq(Y, Z) → eq(X, Z)", "transitivity_xyz")
    
    goal = parser.parse_fact("eq(a, c)")
    initial_facts = {
        parser.parse_fact("eq(a, b)"),
        parser.parse_fact("eq(b, c)")
    }
    
    print(f"Goal: {goal}")
    print(f"Initial facts: {list(initial_facts)}")
    print(f"Rule: {transitivity_rule}")
    
    # Use the engine's forward chainer directly with our custom rule
    result = engine.forward_chainer.prove(goal, initial_facts, [transitivity_rule])
    
    print(f"\nResult: {result}")
    if result.goal_achieved:
        print("\n" + engine.get_proof_explanation(result))
    print("-" * 50)


def demo_multi_step_proof():
    """Demonstrate multi-step proof."""
    print("=== Multi-Step Proof Demo ===")
    
    engine = ProofEngine()
    parser = MathParser()
    
    # Problem: Chain of equalities
    print("\nProblem: If a = b, b = c, and c = d, prove a = d")
    
    # Custom rules for this demo
    transitivity_rule = parser.parse_rule("eq(X, Y) ∧ eq(Y, Z) → eq(X, Z)", "transitivity")
    
    goal = parser.parse_fact("eq(a, d)")
    initial_facts = {
        parser.parse_fact("eq(a, b)"),
        parser.parse_fact("eq(b, c)"),
        parser.parse_fact("eq(c, d)")
    }
    
    print(f"Goal: {goal}")
    print(f"Initial facts: {list(initial_facts)}")
    
    result = engine.forward_chainer.prove(goal, initial_facts, [transitivity_rule])
    
    print(f"\nResult: {result}")
    if result.goal_achieved:
        print("\n" + engine.get_proof_explanation(result))
    print("-" * 50)


def demo_impossible_proof():
    """Demonstrate handling of impossible proofs."""
    print("=== Impossible Proof Demo ===")
    
    engine = ProofEngine()
    parser = MathParser()
    
    # Configure for limited exploration
    engine.configure_engine(max_iterations=5, max_facts=50)
    
    # Problem: Try to prove something impossible
    print("\nProblem: Try to prove x = 10 from y = 5 (impossible)")
    
    goal = parser.parse_fact("eq(x, 10)")
    initial_facts = {parser.parse_fact("eq(y, 5)")}
    
    print(f"Goal: {goal}")
    print(f"Initial facts: {list(initial_facts)}")
    
    result = engine.prove_goal(
        goal, initial_facts,
        specific_rules=["equality_symmetry"]  # Use just one safe rule
    )
    
    print(f"\nResult: {result}")
    print(engine.get_proof_explanation(result))
    print("-" * 50)


def demo_math_problem_solving():
    """Demonstrate solving MathProblem objects."""
    print("=== MathProblem Solving Demo ===")
    
    engine = ProofEngine()
    parser = MathParser()
    
    # Create a MathProblem
    print("\nSolving a structured MathProblem")
    
    facts = [parser.parse_fact("eq(x + 5, 12)")]
    goal = parser.parse_fact("eq(x, 12 - 5)")
    rules = [engine.rule_system.math_rules.get_rule("subtraction_property")]
    
    problem = MathProblem(
        facts=facts,
        rules=rules,
        goal=goal,
        original_text="If x + 5 = 12, find x"
    )
    
    print(f"Problem: {problem.original_text}")
    print(f"Goal: {problem.goal}")
    print(f"Facts: {problem.facts}")
    
    result = engine.solve_problem(problem)
    
    print(f"\nResult: {result}")
    if result.goal_achieved:
        print("\n" + engine.get_proof_explanation(result))
    print("-" * 50)


def demo_engine_statistics():
    """Demonstrate proof engine statistics."""
    print("=== Proof Engine Statistics Demo ===")
    
    engine = ProofEngine()
    parser = MathParser()
    
    # Configure engine for detailed stats
    engine.configure_engine(max_iterations=20, max_facts=100)
    
    # Run a proof
    goal = parser.parse_fact("eq(x, 8 - 2)")
    initial_facts = {parser.parse_fact("eq(x + 2, 8)")}
    
    result = engine.prove_goal(
        goal, initial_facts,
        specific_rules=["subtraction_property", "addition_property", "equality_symmetry"]
    )
    
    print(f"Proof completed: {result.goal_achieved}")
    print(f"Steps taken: {len(result.steps)}")
    print(f"Time elapsed: {result.time_elapsed:.3f}s")
    print(f"Iterations used: {result.iterations_used}")
    print(f"Final facts count: {len(result.final_facts)}")
    
    # Get detailed statistics
    stats = engine.forward_chainer.get_statistics()
    print("\nDetailed Statistics:")
    print(f"- Total iterations: {stats['iterations']}")
    print(f"- Rules applied: {stats['rules_applied']}")
    print(f"- Facts derived: {stats['facts_derived']}")
    if stats['rule_applications']:
        print(f"- Rule usage: {stats['rule_applications']}")
    
    print("-" * 50)


if __name__ == "__main__":
    print("MathGraph Proof Engine Demo")
    print("=" * 60)
    
    demo_basic_algebra_proof()
    demo_transitivity_proof()
    demo_multi_step_proof()
    demo_impossible_proof()
    demo_math_problem_solving()
    demo_engine_statistics()
    
    print("Proof engine demo completed!")