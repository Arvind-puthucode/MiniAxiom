"""
End-to-end integration tests for the MathGraph system.
"""
import pytest
import os
from unittest.mock import patch, Mock
from src.mathgraph import MathReasoningSystem, MathGraphAPI, SystemResponse


def has_azure_credentials():
    """Check if Azure OpenAI credentials are available."""
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    return all(os.getenv(var) for var in required_vars)


@pytest.mark.skipif(not has_azure_credentials(), reason="Azure OpenAI credentials not available")
class TestMathReasoningSystemIntegration:
    """Integration tests with real Azure OpenAI."""
    
    def test_simple_algebra_end_to_end(self):
        """Test complete algebra problem solving pipeline."""
        system = MathReasoningSystem(enable_logging=False)
        
        problem = "If x + 4 = 9, find x"
        
        response = system.solve_problem(problem)
        
        assert response.success == True
        assert response.problem_text == problem
        assert response.formal_problem is not None
        assert response.proof_result is not None
        assert response.explanation is not None
        assert len(response.explanation) > 50  # Should be substantial
        
        # Check metadata
        assert response.metadata is not None
        assert "processing_time" in response.metadata
        assert "problem_type" in response.metadata
        assert response.metadata["problem_type"] in ["algebraic_equation", "algebraic", "equation"]
    
    def test_multiple_problems_batch(self):
        """Test batch processing of multiple problems."""
        system = MathReasoningSystem(enable_logging=False)
        
        problems = [
            "If x + 2 = 5, find x",
            "If 3y = 15, what is y?"
        ]
        
        responses = system.solve_multiple_problems(problems)
        
        assert len(responses) == 2
        for response in responses:
            assert isinstance(response, SystemResponse)
            if response.success:
                assert response.explanation is not None
                assert response.formal_problem is not None
    
    def test_system_statistics(self):
        """Test system statistics tracking."""
        system = MathReasoningSystem(enable_logging=False)
        
        # Solve a problem
        system.solve_problem("If x + 1 = 2, find x")
        
        stats = system.get_system_statistics()
        
        assert "problems_solved" in stats
        assert "problems_failed" in stats
        assert "success_rate" in stats
        assert "average_processing_time" in stats
        assert stats["problems_solved"] + stats["problems_failed"] >= 1
    
    def test_system_configuration(self):
        """Test system configuration."""
        system = MathReasoningSystem(enable_logging=False)
        
        # Configure the system
        config = {
            "max_iterations": 20,
            "max_facts": 200
        }
        system.configure_system(config)
        
        # Verify configuration applied
        assert system.proof_engine.forward_chainer.max_iterations == 20
        assert system.proof_engine.forward_chainer.max_facts == 200
    
    def test_system_validation(self):
        """Test system validation."""
        system = MathReasoningSystem(enable_logging=False)
        
        validation = system.validate_configuration()
        
        assert "valid" in validation
        assert "components" in validation
        assert "llm" in validation["components"]
        assert "parser" in validation["components"]
        assert "proof_engine" in validation["components"]
        
        # Should be valid with proper credentials
        assert validation["valid"] == True


class TestMathReasoningSystemMocked:
    """Test MathReasoningSystem with mocked components."""
    
    def test_error_handling_extraction_failure(self):
        """Test handling of extraction failures."""
        with patch('src.extraction.problem_extractor.ProblemExtractor.extract') as mock_extract:
            mock_extract.side_effect = ValueError("Extraction failed")
            
            system = MathReasoningSystem(enable_logging=False)
            response = system.solve_problem("Invalid problem")
            
            assert response.success == False
            assert "Extraction failed" in response.error_message
            assert response.explanation is not None
    
    def test_error_handling_proof_failure(self):
        """Test handling of proof failures."""
        # Mock successful extraction but failed proof
        mock_problem = Mock()
        mock_problem.metadata = {"problem_type": "test", "confidence": 0.9}
        
        mock_validation = {"is_valid": True, "warnings": []}
        
        mock_proof_result = Mock()
        mock_proof_result.goal_achieved = False
        mock_proof_result.success = True
        
        with patch('src.extraction.problem_extractor.ProblemExtractor.extract', return_value=mock_problem), \
             patch('src.extraction.problem_extractor.ProblemValidator.validate_problem', return_value=mock_validation), \
             patch('src.reasoning.proof_engine.ProofEngine.solve_problem', return_value=mock_proof_result), \
             patch('src.explanation.proof_explainer.ProofExplainer.explain_proof', return_value="Could not solve"):
            
            system = MathReasoningSystem(enable_logging=False)
            response = system.solve_problem("Unsolvable problem")
            
            assert response.success == True  # System succeeded, but proof didn't
            assert response.proof_result.goal_achieved == False
    
    def test_system_response_serialization(self):
        """Test SystemResponse serialization."""
        from src.formal.expressions import MathProblem
        from src.formal.parser import MathParser
        from src.reasoning.proof_engine import ProofResult
        
        parser = MathParser()
        
        # Create mock objects
        fact = parser.parse_fact("eq(x, 5)")
        problem = MathProblem([fact], [], fact, "Test problem")
        proof_result = ProofResult(True, True, [], set(), 1, 0.1)
        
        response = SystemResponse(
            success=True,
            problem_text="Test problem",
            explanation="Test explanation",
            formal_problem=problem,
            proof_result=proof_result,
            metadata={"test": "value"}
        )
        
        # Test serialization
        data = response.to_dict()
        
        assert data["success"] == True
        assert data["problem_text"] == "Test problem"
        assert data["explanation"] == "Test explanation"
        assert data["metadata"]["test"] == "value"
        assert data["formal_representation"] is not None
        assert data["proof_details"] is not None


@pytest.mark.skipif(not has_azure_credentials(), reason="Azure OpenAI credentials not available")
class TestMathGraphAPI:
    """Test the high-level API interface."""
    
    def test_api_solve(self):
        """Test API solve method."""
        api = MathGraphAPI()
        
        result = api.solve("If x + 6 = 10, find x")
        
        assert isinstance(result, dict)
        assert "success" in result
        assert "explanation" in result
        assert "problem_text" in result
    
    def test_api_batch_solve(self):
        """Test API batch solve method."""
        api = MathGraphAPI()
        
        problems = [
            "If x + 1 = 3, find x",
            "If 2y = 8, what is y?"
        ]
        
        results = api.batch_solve(problems)
        
        assert isinstance(results, list)
        assert len(results) == 2
        for result in results:
            assert isinstance(result, dict)
            assert "success" in result
    
    def test_api_health_check(self):
        """Test API health check."""
        api = MathGraphAPI()
        
        health = api.health_check()
        
        assert isinstance(health, dict)
        assert "healthy" in health
        assert "components" in health
        assert "statistics" in health
    
    def test_api_configure(self):
        """Test API configuration."""
        api = MathGraphAPI()
        
        result = api.configure(max_iterations=15)
        
        assert result["status"] == "configured"
        assert result["config"]["max_iterations"] == 15


class TestMathGraphAPIMocked:
    """Test MathGraphAPI with mocked responses."""
    
    def test_api_with_mock_system(self):
        """Test API with mocked system responses."""
        mock_response = SystemResponse(
            success=True,
            problem_text="Test",
            explanation="Test explanation",
            metadata={"test": True}
        )
        
        with patch.object(MathReasoningSystem, 'solve_problem', return_value=mock_response):
            api = MathGraphAPI()
            result = api.solve("Test problem")
            
            assert result["success"] == True
            assert result["explanation"] == "Test explanation"


@pytest.mark.skipif(not has_azure_credentials(), reason="Azure OpenAI credentials not available")
class TestSystemRobustness:
    """Test system robustness and edge cases."""
    
    def test_empty_problem(self):
        """Test handling of empty problems."""
        system = MathReasoningSystem(enable_logging=False)
        
        response = system.solve_problem("")
        
        # Should handle gracefully
        assert response.success == False
        assert response.error_message is not None
    
    def test_non_mathematical_problem(self):
        """Test handling of non-mathematical problems."""
        system = MathReasoningSystem(enable_logging=False)
        
        response = system.solve_problem("What is the weather like?")
        
        # Should either fail extraction or handle gracefully
        assert isinstance(response, SystemResponse)
        # Don't assert success/failure as LLM might handle this differently
    
    def test_system_statistics_reset(self):
        """Test statistics reset functionality."""
        system = MathReasoningSystem(enable_logging=False)
        
        # Solve a problem to generate stats
        system.solve_problem("If x = 1, find x")
        
        # Check stats exist
        stats_before = system.get_system_statistics()
        assert stats_before["problems_solved"] + stats_before["problems_failed"] > 0
        
        # Reset and check
        system.reset_statistics()
        stats_after = system.get_system_statistics()
        assert stats_after["problems_solved"] == 0
        assert stats_after["problems_failed"] == 0


if __name__ == "__main__":
    pytest.main([__file__])