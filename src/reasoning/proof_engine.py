"""
Forward chaining proof engine for mathematical reasoning.

This module implements the systematic proof search algorithm that applies
mathematical rules to derive new facts until a goal is proven or no progress is made.
"""
from typing import Set, List, Optional, Dict, Any
from dataclasses import dataclass
import time

from ..formal.expressions import Fact, Rule
from .pattern_matching import RuleApplicator
from .rules import RuleSystem


@dataclass
class ProofStep:
    """Represents a single step in a proof."""
    rule_applied: Rule
    premises_used: List[Fact]
    derived_fact: Fact
    step_number: int
    
    def __str__(self) -> str:
        premises_str = " ∧ ".join(str(p) for p in self.premises_used)
        return f"Step {self.step_number}: {premises_str} → {self.derived_fact} (using {self.rule_applied.name})"


@dataclass
class ProofResult:
    """Result of a proof attempt."""
    success: bool
    goal_achieved: bool
    steps: List[ProofStep]
    final_facts: Set[Fact]
    iterations_used: int
    time_elapsed: float
    error_message: Optional[str] = None
    
    def __str__(self) -> str:
        if self.success and self.goal_achieved:
            return f"PROOF SUCCESSFUL in {len(self.steps)} steps ({self.time_elapsed:.3f}s)"
        elif self.success:
            return f"No proof found after {self.iterations_used} iterations ({self.time_elapsed:.3f}s)"
        else:
            return f"PROOF FAILED: {self.error_message}"


class ForwardChainer:
    """Forward chaining proof engine implementation."""
    
    def __init__(self, max_iterations: int = 100, max_facts: int = 1000):
        """
        Initialize the forward chainer.
        
        Args:
            max_iterations: Maximum number of inference iterations
            max_facts: Maximum number of facts to maintain (prevents explosion)
        """
        self.max_iterations = max_iterations
        self.max_facts = max_facts
        self.rule_applicator = RuleApplicator()
        
        # Statistics
        self.reset_statistics()
    
    def reset_statistics(self):
        """Reset proof statistics."""
        self.stats = {
            "iterations": 0,
            "rules_applied": 0,
            "facts_derived": 0,
            "rule_applications": {}  # rule_name -> count
        }
    
    def prove(self, goal: Fact, initial_facts: Set[Fact], rules: List[Rule]) -> ProofResult:
        """
        Attempt to prove a goal using forward chaining.
        
        Args:
            goal: The fact we want to prove
            initial_facts: Set of initially known facts
            rules: List of inference rules to use
            
        Returns:
            ProofResult containing success status and proof steps
        """
        start_time = time.time()
        self.reset_statistics()
        
        try:
            # Initialize working facts
            current_facts = initial_facts.copy()
            proof_steps = []
            
            # Check if goal is already proven
            if goal in current_facts:
                elapsed = time.time() - start_time
                return ProofResult(
                    success=True,
                    goal_achieved=True,
                    steps=[],
                    final_facts=current_facts,
                    iterations_used=0,
                    time_elapsed=elapsed
                )
            
            # Main inference loop
            for iteration in range(self.max_iterations):
                self.stats["iterations"] = iteration + 1
                
                # Track progress in this iteration
                facts_at_start = len(current_facts)
                new_facts_this_iteration = []
                
                # Try to apply each rule
                for rule in rules:
                    # Check if we can apply this rule
                    if not self.rule_applicator.can_apply_rule(rule, current_facts):
                        continue
                    
                    # Apply rule and get new facts
                    new_facts = self.rule_applicator.apply_rule(rule, current_facts)
                    
                    for new_fact in new_facts:
                        if new_fact not in current_facts:
                            # Create proof step
                            step = self._create_proof_step(
                                rule, current_facts, new_fact, len(proof_steps) + 1
                            )
                            proof_steps.append(step)
                            
                            # Add to current facts
                            current_facts.add(new_fact)
                            new_facts_this_iteration.append(new_fact)
                            
                            # Update statistics
                            self.stats["facts_derived"] += 1
                            self.stats["rules_applied"] += 1
                            rule_name = rule.name
                            self.stats["rule_applications"][rule_name] = \
                                self.stats["rule_applications"].get(rule_name, 0) + 1
                            
                            # Check if we proved the goal
                            if new_fact == goal:
                                elapsed = time.time() - start_time
                                return ProofResult(
                                    success=True,
                                    goal_achieved=True,
                                    steps=proof_steps,
                                    final_facts=current_facts,
                                    iterations_used=iteration + 1,
                                    time_elapsed=elapsed
                                )
                            
                            # Check fact limit
                            if len(current_facts) > self.max_facts:
                                elapsed = time.time() - start_time
                                return ProofResult(
                                    success=False,
                                    goal_achieved=False,
                                    steps=proof_steps,
                                    final_facts=current_facts,
                                    iterations_used=iteration + 1,
                                    time_elapsed=elapsed,
                                    error_message=f"Too many facts generated (>{self.max_facts})"
                                )
                
                # Check if we made progress
                if len(current_facts) == facts_at_start:
                    # No new facts derived - we're stuck
                    break
            
            # Proof search completed without finding goal
            elapsed = time.time() - start_time
            return ProofResult(
                success=True,
                goal_achieved=False,
                steps=proof_steps,
                final_facts=current_facts,
                iterations_used=self.stats["iterations"],
                time_elapsed=elapsed
            )
            
        except Exception as e:
            elapsed = time.time() - start_time
            return ProofResult(
                success=False,
                goal_achieved=False,
                steps=proof_steps if 'proof_steps' in locals() else [],
                final_facts=current_facts if 'current_facts' in locals() else set(),
                iterations_used=self.stats["iterations"],
                time_elapsed=elapsed,
                error_message=str(e)
            )
    
    def _create_proof_step(self, rule: Rule, current_facts: Set[Fact], 
                          derived_fact: Fact, step_number: int) -> ProofStep:
        """Create a proof step by finding which facts were used as premises."""
        
        # Find the specific facts that matched the rule premises
        rule_matches = self.rule_applicator.pattern_matcher.find_rule_matches(
            rule.premises, current_facts
        )
        
        # There should be at least one match since we just applied the rule
        if not rule_matches:
            # Fallback - this shouldn't happen
            premises_used = list(rule.premises)
        else:
            # Use the first valid substitution to find actual premises
            substitution = rule_matches[0]
            premises_used = []
            
            for premise_pattern in rule.premises:
                # Apply substitution to get the concrete premise
                concrete_premise = substitution.apply_to_fact(premise_pattern)
                if concrete_premise in current_facts:
                    premises_used.append(concrete_premise)
                else:
                    # Fallback to pattern if we can't find exact match
                    premises_used.append(premise_pattern)
        
        return ProofStep(
            rule_applied=rule,
            premises_used=premises_used,
            derived_fact=derived_fact,
            step_number=step_number
        )
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get proof statistics."""
        return self.stats.copy()


class ProofEngine:
    """High-level proof engine interface."""
    
    def __init__(self):
        self.rule_system = RuleSystem()
        self.forward_chainer = ForwardChainer()
    
    def prove_goal(self, goal: Fact, initial_facts: Set[Fact], 
                   rule_categories: Optional[List[str]] = None,
                   specific_rules: Optional[List[str]] = None) -> ProofResult:
        """
        Prove a goal using specified rules.
        
        Args:
            goal: Fact to prove
            initial_facts: Starting facts
            rule_categories: Categories of rules to use (e.g., ['algebraic', 'arithmetic'])
            specific_rules: Specific rule names to use
            
        Returns:
            ProofResult
        """
        # Determine which rules to use
        if specific_rules:
            rules = [self.rule_system.math_rules.get_rule(name) for name in specific_rules]
        elif rule_categories:
            rules = []
            for category in rule_categories:
                rules.extend(self.rule_system.math_rules.get_rules_by_category(category))
        else:
            # Use all active rules
            rules = self.rule_system.get_active_rules()
        
        return self.forward_chainer.prove(goal, initial_facts, rules)
    
    def solve_problem(self, problem) -> ProofResult:
        """
        Solve a MathProblem instance.
        
        Args:
            problem: MathProblem with facts, rules, and goal
            
        Returns:
            ProofResult
        """
        # Convert problem facts to set
        initial_facts = set(problem.facts)
        
        # Use problem-specific rules if provided, otherwise use all active rules
        if problem.rules:
            rules = problem.rules
        else:
            rules = self.rule_system.get_active_rules()
        
        return self.forward_chainer.prove(problem.goal, initial_facts, rules)
    
    def configure_engine(self, max_iterations: int = None, max_facts: int = None):
        """Configure proof engine parameters."""
        if max_iterations is not None:
            self.forward_chainer.max_iterations = max_iterations
        if max_facts is not None:
            self.forward_chainer.max_facts = max_facts
    
    def enable_rules(self, rule_names: List[str]):
        """Enable specific rules."""
        for name in rule_names:
            self.rule_system.enable_rule(name)
    
    def disable_rules(self, rule_names: List[str]):
        """Disable specific rules."""
        for name in rule_names:
            self.rule_system.disable_rule(name)
    
    def get_proof_explanation(self, result: ProofResult) -> str:
        """Generate a human-readable explanation of the proof."""
        if not result.success:
            return f"Proof failed: {result.error_message}"
        
        if not result.goal_achieved:
            return f"Could not prove the goal after {result.iterations_used} iterations and {len(result.steps)} steps."
        
        explanation = [
            f"Proof completed successfully in {len(result.steps)} steps:",
            ""
        ]
        
        for step in result.steps:
            explanation.append(str(step))
        
        explanation.extend([
            "",
            "Statistics:",
            f"- Total iterations: {result.iterations_used}",
            f"- Time elapsed: {result.time_elapsed:.3f} seconds",
            f"- Final facts count: {len(result.final_facts)}"
        ])
        
        return "\n".join(explanation)