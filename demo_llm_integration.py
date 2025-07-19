"""
Demo script showing LLM integration for problem extraction and explanation.
"""
from src.extraction.problem_extractor import ProblemExtractor, ProblemValidator
from src.explanation.proof_explainer import ProofExplainer
from src.reasoning.proof_engine import ProofEngine


def demo_problem_extraction():
    """Demonstrate natural language problem extraction."""
    print("=== Natural Language Problem Extraction Demo ===")
    
    extractor = ProblemExtractor()
    validator = ProblemValidator()
    
    test_problems = [
        "If x + 5 = 12, find x",
        "If n is even, prove that n² is even",
        "If a > b and b > c, prove a > c"
    ]
    
    for problem_text in test_problems:
        print(f"\nProblem: '{problem_text}'")
        try:
            # Extract formal representation
            problem = extractor.extract(problem_text)
            
            print("✓ Extracted successfully!")
            print(f"  Problem type: {problem.metadata.get('problem_type', 'unknown')}")
            print(f"  Confidence: {problem.metadata.get('confidence', 0.0):.2f}")
            print(f"  Facts: {[str(f) for f in problem.facts]}")
            print(f"  Rules: {[str(r) for r in problem.rules]}")
            print(f"  Goal: {problem.goal}")
            
            # Validate the extracted problem
            validation = validator.validate_problem(problem)
            print(f"  Validation: {'✓ Valid' if validation['is_valid'] else '⚠ Issues found'}")
            if validation['warnings']:
                print(f"  Warnings: {validation['warnings']}")
            
        except Exception as e:
            print(f"✗ Extraction failed: {e}")
    
    print("-" * 60)


def demo_end_to_end_solving():
    """Demonstrate end-to-end problem solving with explanations."""
    print("=== End-to-End Problem Solving Demo ===")
    
    extractor = ProblemExtractor()
    proof_engine = ProofEngine()
    explainer = ProofExplainer()
    
    test_problems = [
        "If x + 8 = 15, find x",
        "If 2y = 10, what is y?"
    ]
    
    for problem_text in test_problems:
        print(f"\nSolving: '{problem_text}'")
        print("-" * 40)
        
        try:
            # Step 1: Extract formal problem
            print("Step 1: Extracting formal representation...")
            problem = extractor.extract(problem_text)
            print(f"✓ Extracted as {problem.metadata.get('problem_type', 'unknown')} problem")
            
            # Step 2: Generate problem analysis
            print("\nStep 2: Analyzing problem...")
            validator = ProblemValidator()
            validation = validator.validate_problem(problem)
            analysis = explainer.generate_problem_analysis(problem, validation)
            print(analysis)
            
            # Step 3: Solve the problem
            print("\nStep 3: Solving...")
            result = proof_engine.solve_problem(problem)
            
            if result.goal_achieved:
                print("✓ Successfully solved!")
            else:
                print("⚠ Could not solve completely")
            
            # Step 4: Generate explanation
            print("\nStep 4: Generating explanation...")
            explanation = explainer.explain_proof(problem_text, result)
            print("\n" + "="*50)
            print("EXPLANATION:")
            print("="*50)
            print(explanation)
            
        except Exception as e:
            print(f"✗ Failed: {e}")
        
        print("\n" + "="*60)


def demo_explanation_generation():
    """Demonstrate proof explanation generation."""
    print("=== Proof Explanation Generation Demo ===")
    
    from src.formal.parser import MathParser
    from src.reasoning.proof_engine import ProofResult, ProofStep
    from src.reasoning.rules import RuleSystem
    
    explainer = ProofExplainer()
    parser = MathParser()
    rule_system = RuleSystem()
    
    # Create a sample proof result
    print("\nCreating sample proof for: 'If x + 7 = 12, find x'")
    
    rule = rule_system.math_rules.get_rule("subtraction_property")
    premise = parser.parse_fact("eq(x + 7, 12)")
    derived = parser.parse_fact("eq(x, 12 - 7)")
    
    step = ProofStep(
        rule_applied=rule,
        premises_used=[premise],
        derived_fact=derived,
        step_number=1
    )
    
    result = ProofResult(
        success=True,
        goal_achieved=True,
        steps=[step],
        final_facts={premise, derived},
        iterations_used=1,
        time_elapsed=0.05
    )
    
    # Generate explanation
    try:
        explanation = explainer.explain_proof("If x + 7 = 12, find x", result)
        print("\nGenerated explanation:")
        print("-" * 30)
        print(explanation)
    except Exception as e:
        print(f"✗ Explanation generation failed: {e}")
    
    print("-" * 60)


def demo_single_step_explanation():
    """Demonstrate single step explanation."""
    print("=== Single Step Explanation Demo ===")
    
    from src.formal.parser import MathParser
    from src.reasoning.proof_engine import ProofStep
    from src.reasoning.rules import RuleSystem
    
    explainer = ProofExplainer()
    parser = MathParser()
    rule_system = RuleSystem()
    
    # Create a sample step
    rule = rule_system.math_rules.get_rule("equality_symmetry")
    premise = parser.parse_fact("eq(x, 5)")
    derived = parser.parse_fact("eq(5, x)")
    
    step = ProofStep(
        rule_applied=rule,
        premises_used=[premise],
        derived_fact=derived,
        step_number=1
    )
    
    try:
        explanation = explainer.explain_step(step, "Working with the equation x = 5")
        print(f"\nStep: {step}")
        print(f"Explanation: {explanation}")
    except Exception as e:
        print(f"✗ Step explanation failed: {e}")
    
    print("-" * 60)


def demo_error_handling():
    """Demonstrate error handling and fallbacks."""
    print("=== Error Handling and Fallbacks Demo ===")
    
    extractor = ProblemExtractor()
    
    # Test with an ambiguous/difficult problem
    difficult_problems = [
        "What is the meaning of life?",  # Not a math problem
        "Solve the equation somehow",    # Too vague
        "If unicorns exist, prove they are magical"  # Nonsensical
    ]
    
    for problem_text in difficult_problems:
        print(f"\nTesting: '{problem_text}'")
        try:
            problem = extractor.extract(problem_text)
            print(f"✓ Surprisingly extracted: {problem.metadata.get('problem_type', 'unknown')}")
        except Exception as e:
            print(f"✗ Failed as expected: {e}")
    
    print("-" * 60)


if __name__ == "__main__":
    print("MathGraph LLM Integration Demo")
    print("=" * 70)
    
    try:
        demo_problem_extraction()
        demo_end_to_end_solving()
        demo_explanation_generation()
        demo_single_step_explanation()
        demo_error_handling()
        
        print("LLM integration demo completed successfully!")
        
    except Exception as e:
        print(f"Demo failed: {e}")
        print("Please ensure Azure OpenAI credentials are properly configured in .env file")