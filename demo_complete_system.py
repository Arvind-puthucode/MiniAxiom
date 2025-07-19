"""
Complete MathGraph System Demo

This demo showcases the full hybrid mathematical reasoning system
from natural language input to formal proof to natural language explanation.
"""
from src.mathgraph import MathReasoningSystem, MathGraphAPI
import json


def demo_complete_pipeline():
    """Demonstrate the complete mathematical reasoning pipeline."""
    print("=== Complete MathGraph Pipeline Demo ===")
    
    system = MathReasoningSystem(enable_logging=False)
    
    # Test problems across different mathematical domains
    test_problems = [
        "If x + 7 = 15, find x",
        "If 3y = 21, what is y?",
        "If n is even, prove that 2n is even",
        "If a > b and b > c, prove a > c"
    ]
    
    for i, problem in enumerate(test_problems, 1):
        print(f"\n{'='*60}")
        print(f"PROBLEM {i}: {problem}")
        print('='*60)
        
        try:
            # Process the problem through the complete pipeline
            response = system.solve_problem(problem, {
                "show_analysis": True,
                "max_steps": 20
            })
            
            if response.success:
                print(f"✓ SUCCESS: {response.metadata['problem_type']} problem solved!")
                print(f"  Confidence: {response.metadata['extraction_confidence']:.2f}")
                print(f"  Processing time: {response.metadata['processing_time']:.3f}s")
                
                if response.analysis:
                    print("\nPROBLEM ANALYSIS:")
                    print("-" * 20)
                    print(response.analysis)
                
                print("\nFORMAL REPRESENTATION:")
                print("-" * 25)
                print(f"Facts: {[str(f) for f in response.formal_problem.facts]}")
                print(f"Rules: {[r.name for r in response.formal_problem.rules]}")
                print(f"Goal: {response.formal_problem.goal}")
                
                if response.proof_result.goal_achieved:
                    print("\nPROOF SUCCESSFUL:")
                    print("-" * 20)
                    print(f"Steps: {len(response.proof_result.steps)}")
                    print(f"Iterations: {response.proof_result.iterations_used}")
                    print(f"Time: {response.proof_result.time_elapsed:.3f}s")
                    
                    # Show formal proof steps
                    print("\nFORMAL PROOF STEPS:")
                    for step in response.proof_result.steps:
                        print(f"  {step}")
                else:
                    print("\nPROOF INCOMPLETE:")
                    print("-" * 20)
                    print(f"Explored {len(response.proof_result.final_facts)} facts")
                    print(f"Made {len(response.proof_result.steps)} inference steps")
                
                print("\nNATURAL LANGUAGE EXPLANATION:")
                print("-" * 35)
                print(response.explanation)
                
            else:
                print(f"✗ FAILED: {response.error_message}")
                
        except Exception as e:
            print(f"✗ ERROR: {e}")


def demo_api_interface():
    """Demonstrate the high-level API interface."""
    print("\n" + "="*60)
    print("HIGH-LEVEL API DEMO")
    print("="*60)
    
    api = MathGraphAPI()
    
    # Health check
    print("\n1. SYSTEM HEALTH CHECK:")
    health = api.health_check()
    print(f"   Healthy: {health['healthy']}")
    print(f"   Components: {list(health['components'].keys())}")
    if health['issues']:
        print(f"   Issues: {health['issues']}")
    
    # Solve single problem
    print("\n2. SINGLE PROBLEM SOLVING:")
    problem = "If x - 3 = 7, find x"
    result = api.solve(problem)
    print(f"   Problem: {problem}")
    print(f"   Success: {result['success']}")
    if result['success'] and result['proof_details']:
        print(f"   Goal achieved: {result['proof_details']['goal_achieved']}")
        print(f"   Steps: {result['proof_details']['steps_count']}")
    
    # Batch solving
    print("\n3. BATCH PROBLEM SOLVING:")
    problems = [
        "If 2x = 14, find x",
        "If y + 4 = 12, find y"
    ]
    results = api.batch_solve(problems)
    print(f"   Processed {len(results)} problems")
    successful = sum(1 for r in results if r['success'])
    print(f"   Successful: {successful}/{len(results)}")
    
    # Configuration
    print("\n4. SYSTEM CONFIGURATION:")
    config_result = api.configure(max_iterations=25, max_facts=150)
    print(f"   Configuration: {config_result['status']}")
    print(f"   Applied settings: {config_result['config']}")


def demo_problem_types():
    """Demonstrate different types of mathematical problems."""
    print("\n" + "="*60)
    print("MATHEMATICAL PROBLEM TYPES DEMO")
    print("="*60)
    
    system = MathReasoningSystem(enable_logging=False)
    
    problem_categories = {
        "Linear Equations": [
            "If x + 5 = 13, find x",
            "If 4y = 32, what is y?",
            "If z - 8 = 2, find z"
        ],
        "Arithmetic Properties": [
            "If n is even, prove that n + 2 is even",
            "If a is odd and b is odd, prove that a + b is even"
        ],
        "Inequalities": [
            "If x > 5 and 5 > 3, prove x > 3",
            "If a > b and b > 0, prove a > 0"
        ]
    }
    
    for category, problems in problem_categories.items():
        print(f"\n{category.upper()}:")
        print("-" * len(category))
        
        for problem in problems:
            try:
                response = system.solve_problem(problem)
                status = "✓" if response.success and response.proof_result.goal_achieved else "⚠"
                problem_type = response.metadata.get('problem_type', 'unknown') if response.metadata else 'unknown'
                print(f"  {status} {problem} [{problem_type}]")
                
            except Exception as e:
                print(f"  ✗ {problem} [error: {str(e)[:50]}...]")


def demo_system_performance():
    """Demonstrate system performance and statistics."""
    print("\n" + "="*60)
    print("SYSTEM PERFORMANCE DEMO")
    print("="*60)
    
    system = MathReasoningSystem(enable_logging=False)
    
    # Test a variety of problems to generate statistics
    test_problems = [
        "If x + 1 = 5, find x",
        "If 2y = 16, what is y?",
        "If z - 3 = 9, find z",
        "If 5a = 45, what is a?",
        "If b + 7 = 20, find b"
    ]
    
    print(f"Processing {len(test_problems)} problems...")
    
    successful = 0
    total_time = 0
    
    for problem in test_problems:
        try:
            response = system.solve_problem(problem)
            if response.success and response.proof_result.goal_achieved:
                successful += 1
            if response.metadata:
                total_time += response.metadata.get('processing_time', 0)
        except Exception:
            pass
    
    # Get system statistics
    stats = system.get_system_statistics()
    
    print("\nPERFORMANCE RESULTS:")
    print(f"  Total problems processed: {stats['problems_solved'] + stats['problems_failed']}")
    print(f"  Successfully solved: {stats['problems_solved']}")
    print(f"  Failed: {stats['problems_failed']}")
    print(f"  Success rate: {stats['success_rate']:.1%}")
    print(f"  Average processing time: {stats['average_processing_time']:.3f}s")
    print(f"  Total processing time: {stats['total_processing_time']:.3f}s")
    print(f"  Successful extractions: {stats['successful_extractions']}")
    print(f"  Successful proofs: {stats['successful_proofs']}")


def demo_error_handling():
    """Demonstrate error handling and edge cases."""
    print("\n" + "="*60)
    print("ERROR HANDLING & EDGE CASES DEMO")
    print("="*60)
    
    system = MathReasoningSystem(enable_logging=False)
    
    edge_cases = [
        ("Empty problem", ""),
        ("Non-mathematical", "What is the weather today?"),
        ("Ambiguous", "Solve something"),
        ("Impossible equation", "If x + 1 = x + 2, find x"),
        ("Complex problem", "Prove that the square root of 2 is irrational")
    ]
    
    for description, problem in edge_cases:
        print(f"\n{description}: '{problem}'")
        try:
            response = system.solve_problem(problem)
            if response.success:
                if response.proof_result and response.proof_result.goal_achieved:
                    print("  ✓ Surprisingly solved!")
                else:
                    print("  ⚠ Processed but couldn't solve")
            else:
                print(f"  ✗ Failed as expected: {response.error_message[:50]}...")
        except Exception as e:
            print(f"  ✗ Exception: {str(e)[:50]}...")


def demo_serialization():
    """Demonstrate response serialization for API usage."""
    print("\n" + "="*60)
    print("RESPONSE SERIALIZATION DEMO")
    print("="*60)
    
    system = MathReasoningSystem(enable_logging=False)
    
    problem = "If x + 9 = 17, find x"
    response = system.solve_problem(problem)
    
    # Convert to dictionary for JSON serialization
    response_dict = response.to_dict()
    
    print(f"Problem: {problem}")
    print("Serialized response structure:")
    print(f"  Keys: {list(response_dict.keys())}")
    
    if response_dict['formal_representation']:
        print("  Formal representation included: ✓")
    
    if response_dict['proof_details']:
        print("  Proof details included: ✓")
        print(f"  Goal achieved: {response_dict['proof_details']['goal_achieved']}")
    
    # Show how it would look as JSON (truncated)
    json_str = json.dumps(response_dict, indent=2)
    print(f"\nJSON size: {len(json_str)} characters")
    print("First 200 characters of JSON:")
    print(json_str[:200] + "..." if len(json_str) > 200 else json_str)


if __name__ == "__main__":
    print("MathGraph: Complete Hybrid Mathematical Reasoning System")
    print("=" * 80)
    print("Demonstrating end-to-end pipeline from natural language to formal proof")
    print("=" * 80)
    
    try:
        demo_complete_pipeline()
        demo_api_interface()
        demo_problem_types()
        demo_system_performance()
        demo_error_handling()
        demo_serialization()
        
        print("\n" + "="*80)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("The MathGraph system successfully demonstrates:")
        print("• Natural language problem extraction")
        print("• Formal mathematical reasoning")
        print("• Automated proof generation")
        print("• Natural language explanation")
        print("• Hybrid LLM + symbolic reasoning approach")
        print("="*80)
        
    except Exception as e:
        print(f"\nDemo failed: {e}")
        print("Please ensure Azure OpenAI credentials are properly configured.")