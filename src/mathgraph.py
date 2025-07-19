"""
MathGraph: Hybrid Mathematical Reasoning System

This is the main system integration module that combines all components
into a unified mathematical reasoning system.
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import time
import logging

from .extraction.problem_extractor import ProblemExtractor, ProblemValidator
from .reasoning.proof_engine import ProofEngine, ProofResult
from .explanation.proof_explainer import ProofExplainer
from .formal.expressions import MathProblem


@dataclass
class SystemResponse:
    """Response from the mathematical reasoning system."""
    success: bool
    problem_text: str
    explanation: str
    formal_problem: Optional[MathProblem] = None
    proof_result: Optional[ProofResult] = None
    analysis: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary for serialization."""
        return {
            "success": self.success,
            "problem_text": self.problem_text,
            "explanation": self.explanation,
            "analysis": self.analysis,
            "error_message": self.error_message,
            "metadata": self.metadata or {},
            "formal_representation": {
                "facts": [str(f) for f in self.formal_problem.facts] if self.formal_problem else [],
                "rules": [str(r) for r in self.formal_problem.rules] if self.formal_problem else [],
                "goal": str(self.formal_problem.goal) if self.formal_problem else None
            } if self.formal_problem else None,
            "proof_details": {
                "goal_achieved": self.proof_result.goal_achieved if self.proof_result else False,
                "steps_count": len(self.proof_result.steps) if self.proof_result else 0,
                "time_elapsed": self.proof_result.time_elapsed if self.proof_result else 0.0,
                "iterations_used": self.proof_result.iterations_used if self.proof_result else 0
            } if self.proof_result else None
        }


class MathReasoningSystem:
    """Main mathematical reasoning system that integrates all components."""
    
    def __init__(self, enable_logging: bool = True):
        """
        Initialize the mathematical reasoning system.
        
        Args:
            enable_logging: Whether to enable detailed logging
        """
        self.problem_extractor = ProblemExtractor()
        self.problem_validator = ProblemValidator()
        self.proof_engine = ProofEngine()
        self.proof_explainer = ProofExplainer()
        
        # Configure logging
        if enable_logging:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        self.logger = logging.getLogger(__name__)
        
        # System statistics
        self.stats = {
            "problems_solved": 0,
            "problems_failed": 0,
            "total_processing_time": 0.0,
            "successful_extractions": 0,
            "successful_proofs": 0
        }
    
    def solve_problem(self, natural_language: str, 
                     options: Optional[Dict[str, Any]] = None) -> SystemResponse:
        """
        Solve a mathematical problem from natural language.
        
        Args:
            natural_language: Natural language description of the problem
            options: Optional configuration (max_steps, show_intermediate, etc.)
            
        Returns:
            SystemResponse with solution or error information
        """
        start_time = time.time()
        options = options or {}
        
        self.logger.info(f"Processing problem: {natural_language}")
        
        try:
            # Stage 1: Extract formal representation
            self.logger.info("Stage 1: Extracting formal representation")
            formal_problem = self.problem_extractor.extract(natural_language)
            self.stats["successful_extractions"] += 1
            
            self.logger.info(f"Extracted as {formal_problem.metadata.get('problem_type', 'unknown')} problem")
            
            # Stage 2: Validate extraction
            self.logger.info("Stage 2: Validating extraction")
            validation_results = self.problem_validator.validate_problem(formal_problem)
            
            if not validation_results["is_valid"]:
                return self._create_error_response(
                    natural_language, 
                    f"Invalid problem extraction: {validation_results['errors']}",
                    formal_problem=formal_problem
                )
            
            # Stage 3: Generate problem analysis
            analysis = None
            if options.get("show_analysis", True):
                self.logger.info("Stage 3: Generating problem analysis")
                try:
                    analysis = self.proof_explainer.generate_problem_analysis(
                        formal_problem, validation_results
                    )
                except Exception as e:
                    self.logger.warning(f"Analysis generation failed: {e}")
                    analysis = "Problem analysis unavailable."
            
            # Stage 4: Configure proof engine
            if options.get("max_steps"):
                self.proof_engine.configure_engine(max_iterations=options["max_steps"])
            
            # Stage 5: Attempt proof
            self.logger.info("Stage 4: Attempting proof")
            proof_result = self.proof_engine.solve_problem(formal_problem)
            
            # Stage 6: Generate explanation
            self.logger.info("Stage 5: Generating explanation")
            if proof_result.goal_achieved:
                explanation = self.proof_explainer.explain_proof(natural_language, proof_result)
                self.stats["successful_proofs"] += 1
            else:
                explanation = self.proof_explainer.explain_proof(natural_language, proof_result)
            
            # Update statistics
            elapsed_time = time.time() - start_time
            self.stats["total_processing_time"] += elapsed_time
            
            if proof_result.goal_achieved:
                self.stats["problems_solved"] += 1
            else:
                self.stats["problems_failed"] += 1
            
            # Create response
            metadata = {
                "processing_time": elapsed_time,
                "extraction_confidence": formal_problem.metadata.get("confidence", 0.0),
                "problem_type": formal_problem.metadata.get("problem_type", "unknown"),
                "validation_warnings": validation_results.get("warnings", []),
                "proof_statistics": self.proof_engine.forward_chainer.get_statistics()
            }
            
            return SystemResponse(
                success=True,
                problem_text=natural_language,
                explanation=explanation,
                formal_problem=formal_problem,
                proof_result=proof_result,
                analysis=analysis,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"System error processing '{natural_language}': {str(e)}")
            self.stats["problems_failed"] += 1
            
            return self._create_error_response(natural_language, str(e))
    
    def _create_error_response(self, problem_text: str, error_message: str, 
                             formal_problem: Optional[MathProblem] = None) -> SystemResponse:
        """Create an error response."""
        return SystemResponse(
            success=False,
            problem_text=problem_text,
            explanation=f"I was unable to solve this problem: {error_message}",
            formal_problem=formal_problem,
            error_message=error_message,
            metadata={"processing_time": 0.0, "error_type": "system_error"}
        )
    
    def solve_multiple_problems(self, problems: List[str], 
                               options: Optional[Dict[str, Any]] = None) -> List[SystemResponse]:
        """
        Solve multiple problems in batch.
        
        Args:
            problems: List of natural language problem descriptions
            options: Optional configuration
            
        Returns:
            List of SystemResponse objects
        """
        results = []
        for i, problem in enumerate(problems):
            self.logger.info(f"Solving problem {i+1}/{len(problems)}")
            result = self.solve_problem(problem, options)
            results.append(result)
        
        return results
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system performance statistics."""
        return {
            **self.stats,
            "success_rate": (
                self.stats["problems_solved"] / 
                max(1, self.stats["problems_solved"] + self.stats["problems_failed"])
            ),
            "average_processing_time": (
                self.stats["total_processing_time"] / 
                max(1, self.stats["problems_solved"] + self.stats["problems_failed"])
            )
        }
    
    def configure_system(self, config: Dict[str, Any]):
        """
        Configure system components.
        
        Args:
            config: Configuration dictionary with component settings
        """
        # Configure proof engine
        if "max_iterations" in config:
            self.proof_engine.configure_engine(max_iterations=config["max_iterations"])
        if "max_facts" in config:
            self.proof_engine.configure_engine(max_facts=config["max_facts"])
        
        # Configure rule system
        if "disabled_rules" in config:
            self.proof_engine.disable_rules(config["disabled_rules"])
        if "enabled_rules" in config:
            self.proof_engine.enable_rules(config["enabled_rules"])
        
        self.logger.info("System configuration updated")
    
    def reset_statistics(self):
        """Reset system statistics."""
        self.stats = {
            "problems_solved": 0,
            "problems_failed": 0,
            "total_processing_time": 0.0,
            "successful_extractions": 0,
            "successful_proofs": 0
        }
        self.logger.info("System statistics reset")
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate system configuration and dependencies.
        
        Returns:
            Validation results with status and any issues
        """
        results = {
            "valid": True,
            "issues": [],
            "components": {}
        }
        
        # Test LLM connection
        try:
            test_connected = self.problem_extractor.llm_client.test_connection()
            results["components"]["llm"] = {
                "status": "connected" if test_connected else "disconnected",
                "working": test_connected
            }
            if not test_connected:
                results["issues"].append("Azure OpenAI connection failed")
                results["valid"] = False
        except Exception as e:
            results["components"]["llm"] = {"status": "error", "error": str(e), "working": False}
            results["issues"].append(f"LLM initialization error: {e}")
            results["valid"] = False
        
        # Test parser
        try:
            from .formal.parser import MathParser
            parser = MathParser()
            test_expr = parser.parse_expression("x + 1")
            results["components"]["parser"] = {"status": "working", "working": True}
        except Exception as e:
            results["components"]["parser"] = {"status": "error", "error": str(e), "working": False}
            results["issues"].append(f"Parser error: {e}")
            results["valid"] = False
        
        # Test proof engine
        try:
            engine_stats = self.proof_engine.forward_chainer.get_statistics()
            results["components"]["proof_engine"] = {"status": "ready", "working": True}
        except Exception as e:
            results["components"]["proof_engine"] = {"status": "error", "error": str(e), "working": False}
            results["issues"].append(f"Proof engine error: {e}")
            results["valid"] = False
        
        return results


class MathGraphAPI:
    """High-level API interface for the MathGraph system."""
    
    def __init__(self):
        self.system = MathReasoningSystem()
    
    def solve(self, problem: str, **kwargs) -> Dict[str, Any]:
        """
        Solve a mathematical problem (simplified API).
        
        Args:
            problem: Natural language problem description
            **kwargs: Additional options
            
        Returns:
            Dictionary with solution results
        """
        response = self.system.solve_problem(problem, kwargs)
        return response.to_dict()
    
    def batch_solve(self, problems: List[str], **kwargs) -> List[Dict[str, Any]]:
        """
        Solve multiple problems in batch.
        
        Args:
            problems: List of problem descriptions
            **kwargs: Additional options
            
        Returns:
            List of solution dictionaries
        """
        responses = self.system.solve_multiple_problems(problems, kwargs)
        return [response.to_dict() for response in responses]
    
    def health_check(self) -> Dict[str, Any]:
        """
        Check system health and configuration.
        
        Returns:
            System health status
        """
        validation = self.system.validate_configuration()
        stats = self.system.get_system_statistics()
        
        return {
            "healthy": validation["valid"],
            "issues": validation["issues"],
            "components": validation["components"],
            "statistics": stats
        }
    
    def configure(self, **config):
        """Configure the system with given parameters."""
        self.system.configure_system(config)
        return {"status": "configured", "config": config}