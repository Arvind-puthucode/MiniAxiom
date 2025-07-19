"""
Demo script showing the core mathematical reasoning system in action.
"""
from src.formal.parser import MathParser
from src.reasoning.pattern_matching import RuleApplicator
from src.reasoning.rules import RuleSystem


def demo_basic_algebra():
    """Demonstrate basic algebraic reasoning."""
    print("=== Basic Algebraic Reasoning Demo ===")
    
    # Initialize components
    parser = MathParser()
    rule_system = RuleSystem()
    applicator = RuleApplicator()
    
    # Problem: If x + 3 = 7, what is x?
    print("\nProblem: If x + 3 = 7, what is x?")
    
    # Initial fact: eq(x + 3, 7)
    initial_fact = parser.parse_fact("eq(x + 3, 7)")
    print(f"Initial fact: {initial_fact}")
    
    # Get subtraction property rule
    subtraction_rule = rule_system.math_rules.get_rule("subtraction_property")
    print(f"Rule: {subtraction_rule}")
    
    # Apply rule
    available_facts = {initial_fact}
    new_facts = applicator.apply_rule(subtraction_rule, available_facts)
    
    print(f"New facts derived: {new_facts}")
    if new_facts:
        print(f"Solution: {new_facts[0]}")
    print()


def demo_transitivity():
    """Demonstrate transitivity reasoning."""
    print("=== Transitivity Reasoning Demo ===")
    
    parser = MathParser()
    rule_system = RuleSystem()
    applicator = RuleApplicator()
    
    # Problem: If a = b and b = c, then a = c
    print("\nProblem: If a = b and b = c, then a = c")
    
    # Initial facts
    fact1 = parser.parse_fact("eq(a, b)")
    fact2 = parser.parse_fact("eq(b, c)")
    print(f"Facts: {fact1}, {fact2}")
    
    # Get transitivity rule
    transitivity_rule = rule_system.math_rules.get_rule("equality_transitivity")
    print(f"Rule: {transitivity_rule}")
    
    # Apply rule
    available_facts = {fact1, fact2}
    new_facts = applicator.apply_rule(transitivity_rule, available_facts)
    
    print(f"New facts derived: {new_facts}")
    if new_facts:
        print(f"Conclusion: {new_facts[0]}")
    print()


def demo_rule_categories():
    """Demonstrate different rule categories."""
    print("=== Rule Categories Demo ===")
    
    rule_system = RuleSystem()
    
    categories = ["algebraic", "arithmetic", "comparison", "number_theory"]
    
    for category in categories:
        rules = rule_system.math_rules.get_rules_by_category(category)
        print(f"\n{category.title()} Rules ({len(rules)} total):")
        for rule in rules[:3]:  # Show first 3 rules
            print(f"  - {rule.name}: {rule}")
        if len(rules) > 3:
            print(f"  ... and {len(rules) - 3} more")
    print()


def demo_pattern_matching():
    """Demonstrate pattern matching capabilities."""
    print("=== Pattern Matching Demo ===")
    
    from src.reasoning.pattern_matching import PatternMatcher
    
    matcher = PatternMatcher()
    parser = MathParser()
    
    # Pattern: X + A
    pattern = parser.parse_expression("X + A")
    
    # Target expressions to match
    targets = [
        "y + 3",
        "z + 5",
        "a + b"
    ]
    
    print(f"Pattern: {pattern}")
    print("Matching against:")
    
    for target_str in targets:
        target = parser.parse_expression(target_str)
        result = matcher.match_expression(pattern, target)
        print(f"  {target_str} -> {result}")
    print()


if __name__ == "__main__":
    print("MathGraph Core System Demo")
    print("=" * 50)
    
    demo_basic_algebra()
    demo_transitivity()
    demo_pattern_matching()
    demo_rule_categories()
    
    print("Demo completed! Core mathematical reasoning system is working.")