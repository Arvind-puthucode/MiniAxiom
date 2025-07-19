"""
LLM-based proof explanation generation.

This module uses Azure OpenAI to convert formal proof steps into clear,
educational natural language explanations.
"""
from typing import List, Dict, Any
from ..reasoning.proof_engine import ProofResult, ProofStep
from ..extraction.llm_client import AzureOpenAIClient


class ProofExplainer:
    """Generate natural language explanations of mathematical proofs."""
    
    def __init__(self):
        self.llm_client = AzureOpenAIClient()
        
        # Template for explanation generation
        self.explanation_template = """
You are an expert mathematics tutor. Convert this formal mathematical proof into a clear, educational explanation.

Original Problem: {original_problem}

Formal Proof Steps:
{formatted_steps}

REQUIREMENTS:
1. Write for high school to early college level understanding
2. Explain the logical reasoning at each step clearly
3. Use proper mathematical terminology
4. Show the connection between steps
5. Make it educational and engaging
6. End with a clear conclusion statement

STRUCTURE:
- Start with "To solve this problem..."
- For each step: "Next, we apply [rule name] because..."
- Connect steps with transitional phrases
- End with "Therefore, we have proven that..."

TONE:
- Clear and confident
- Educational but not condescending  
- Show the logical flow of reasoning
- Explain why each step is valid

Generate the explanation now:
"""
    
    def explain_proof(self, problem_text: str, proof_result: ProofResult) -> str:
        """
        Generate a natural language explanation of a proof.
        
        Args:
            problem_text: Original problem statement in natural language
            proof_result: Result from the proof engine
            
        Returns:
            Natural language explanation of the proof
        """
        try:
            if not proof_result.success:
                return self._explain_failed_proof(problem_text, proof_result)
            
            if not proof_result.goal_achieved:
                return self._explain_incomplete_proof(problem_text, proof_result)
            
            # Format proof steps for the LLM
            formatted_steps = self._format_proof_steps(proof_result.steps)
            
            # Generate explanation prompt
            prompt = self.explanation_template.format(
                original_problem=problem_text,
                formatted_steps=formatted_steps
            )
            
            # Get explanation from LLM
            explanation = self.llm_client.generate_completion(prompt, max_tokens=1000, temperature=0.3)
            
            # Add metadata footer
            footer = self._generate_footer(proof_result)
            
            return explanation + "\n\n" + footer
            
        except Exception as e:
            # Fallback to basic explanation
            return self._generate_fallback_explanation(problem_text, proof_result, str(e))
    
    def _format_proof_steps(self, steps: List[ProofStep]) -> str:
        """Format proof steps for the LLM prompt."""
        if not steps:
            return "No proof steps (goal was already proven from initial facts)."
        
        formatted = []
        for i, step in enumerate(steps, 1):
            premises_str = " and ".join(str(p) for p in step.premises_used)
            formatted.append(
                f"Step {i}: From {premises_str}, "
                f"using {step.rule_applied.name}, "
                f"we derive {step.derived_fact}"
            )
        
        return "\n".join(formatted)
    
    def _explain_failed_proof(self, problem_text: str, proof_result: ProofResult) -> str:
        """Generate explanation for a failed proof."""
        return f"""
I was unable to solve this problem: "{problem_text}"

The proof attempt failed due to: {proof_result.error_message}

This could happen for several reasons:
1. The problem might need additional facts or assumptions
2. The required mathematical rules might not be available in the system
3. The problem might be stated in a way that's difficult to formalize
4. There might be an error in how the problem was interpreted

To help solve this problem, you could try:
- Providing more context or background information
- Breaking the problem into smaller steps
- Stating any additional facts or assumptions that should be used
"""
    
    def _explain_incomplete_proof(self, problem_text: str, proof_result: ProofResult) -> str:
        """Generate explanation for an incomplete proof."""
        explanation = f'I attempted to solve: "{problem_text}"\n\n'
        
        if proof_result.steps:
            explanation += "I was able to make some progress:\n\n"
            for i, step in enumerate(proof_result.steps, 1):
                explanation += f"Step {i}: Using {step.rule_applied.name}, "
                explanation += f"I derived that {step.derived_fact}\n"
            
            explanation += f"\nHowever, I could not reach the final goal after {proof_result.iterations_used} iterations. "
        else:
            explanation += "Unfortunately, I could not make any progress toward solving this problem. "
        
        explanation += """
This might mean:
1. Additional mathematical rules or facts are needed
2. The problem requires a more sophisticated reasoning approach
3. The goal might not be derivable from the given information

The reasoning engine explored {} facts before stopping.""".format(len(proof_result.final_facts))
        
        return explanation
    
    def _generate_footer(self, proof_result: ProofResult) -> str:
        """Generate metadata footer for successful proofs."""
        return f"""---
Proof completed in {len(proof_result.steps)} logical steps using formal mathematical reasoning.
Time: {proof_result.time_elapsed:.3f} seconds | Iterations: {proof_result.iterations_used}"""
    
    def _generate_fallback_explanation(self, problem_text: str, proof_result: ProofResult, error: str) -> str:
        """Generate a basic fallback explanation when LLM fails."""
        if not proof_result.success:
            return f"Failed to solve '{problem_text}': {proof_result.error_message}"
        
        if not proof_result.goal_achieved:
            return f"Could not prove the goal for '{problem_text}' after {proof_result.iterations_used} iterations."
        
        # Basic step-by-step explanation
        explanation = f"Successfully solved: {problem_text}\n\nProof steps:\n"
        for i, step in enumerate(proof_result.steps, 1):
            explanation += f"{i}. Applied {step.rule_applied.name} to derive {step.derived_fact}\n"
        
        explanation += f"\nNote: Detailed explanation generation failed ({error}), showing basic proof structure."
        
        return explanation
    
    def explain_step(self, step: ProofStep, context: str = "") -> str:
        """
        Generate explanation for a single proof step.
        
        Args:
            step: ProofStep to explain
            context: Additional context about the problem
            
        Returns:
            Natural language explanation of the step
        """
        prompt = f"""
Explain this single mathematical reasoning step in simple terms:

{context}

Step: From {' and '.join(str(p) for p in step.premises_used)}, 
using the rule "{step.rule_applied.name}", 
we can conclude that {step.derived_fact}.

Provide a clear, concise explanation of why this step is valid and what it means mathematically.
"""
        
        try:
            return self.llm_client.generate_completion(prompt, max_tokens=200, temperature=0.2)
        except Exception:
            # Fallback explanation
            return f"By applying the {step.rule_applied.name} rule, we can derive {step.derived_fact}."
    
    def generate_problem_analysis(self, problem, validation_results: Dict[str, Any]) -> str:
        """
        Generate analysis of a mathematical problem before solving.
        
        Args:
            problem: MathProblem object
            validation_results: Results from problem validation
            
        Returns:
            Natural language analysis of the problem
        """
        prompt = f"""
Analyze this mathematical problem and explain the approach needed to solve it:

Problem: {problem.original_text}
Facts: {[str(f) for f in problem.facts]}
Goal: {problem.goal}
Available Rules: {[r.name for r in problem.rules]}

Problem Type: {problem.metadata.get('problem_type', 'unknown')}
Validation Status: {'Valid' if validation_results['is_valid'] else 'Has issues'}

Provide a brief analysis covering:
1. What type of mathematical problem this is
2. What approach would be needed to solve it
3. What the expected outcome should be
4. Any potential challenges or considerations

Keep it concise but informative.
"""
        
        try:
            return self.llm_client.generate_completion(prompt, max_tokens=400, temperature=0.3)
        except Exception:
            # Fallback analysis
            problem_type = problem.metadata.get('problem_type', 'mathematical')
            return f"""
This is a {problem_type} problem that asks us to prove {problem.goal} from the given facts.

The problem provides {len(problem.facts)} initial fact(s) and {len(problem.rules)} reasoning rule(s).
{"The problem appears to be well-formed." if validation_results['is_valid'] else "There may be some issues with the problem formulation."}

We'll attempt to use logical reasoning to derive the goal from the given information.
"""