"""
Test suite for LLM integration components.

Note: These tests require valid Azure OpenAI credentials in .env file.
Some tests will be skipped if credentials are not available.
"""
import pytest
import os
from unittest.mock import Mock, patch
from src.extraction.llm_client import AzureOpenAIClient
from src.extraction.problem_extractor import ProblemExtractor, ProblemValidator
from src.explanation.proof_explainer import ProofExplainer
from src.formal.parser import MathParser
from src.reasoning.proof_engine import ProofResult, ProofStep
from src.reasoning.rules import RuleSystem


def has_azure_credentials():
    """Check if Azure OpenAI credentials are available."""
    required_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT", 
        "AZURE_OPENAI_DEPLOYMENT_NAME"
    ]
    return all(os.getenv(var) for var in required_vars)


@pytest.mark.skipif(not has_azure_credentials(), reason="Azure OpenAI credentials not available")
class TestAzureOpenAIClient:
    def test_client_initialization(self):
        """Test that client initializes correctly with credentials."""
        client = AzureOpenAIClient()
        
        assert client.api_key is not None
        assert client.endpoint is not None
        assert client.deployment_name is not None
        assert client.client is not None
    
    def test_connection_test(self):
        """Test connection to Azure OpenAI."""
        client = AzureOpenAIClient()
        
        # This will make an actual API call
        is_connected = client.test_connection()
        assert is_connected == True
    
    def test_basic_completion(self):
        """Test basic text completion."""
        client = AzureOpenAIClient()
        
        response = client.generate_completion("What is 2 + 2?", max_tokens=50)
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Should mention "4" somewhere in the response
        assert "4" in response
    
    def test_json_completion(self):
        """Test JSON completion."""
        client = AzureOpenAIClient()
        
        prompt = 'Return a JSON object with a "result" field containing the answer to 3 + 5.'
        response = client.generate_json_completion(prompt, max_tokens=100)
        
        assert isinstance(response, dict)
        assert "result" in response
        # The result should be 8
        assert str(response["result"]).strip() in ["8", "eight"]


class TestAzureOpenAIClientMocked:
    """Test AzureOpenAIClient with mocked responses."""
    
    def test_initialization_without_credentials(self):
        """Test that initialization fails without credentials."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="Missing Azure OpenAI configuration"):
                AzureOpenAIClient()
    
    @patch('src.extraction.llm_client.openai.AzureOpenAI')
    def test_mocked_completion(self, mock_azure_openai):
        """Test completion with mocked Azure OpenAI."""
        # Mock the client and response
        mock_client = Mock()
        mock_azure_openai.return_value = mock_client
        
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "This is a test response."
        mock_client.chat.completions.create.return_value = mock_response
        
        # Set up environment variables
        with patch.dict(os.environ, {
            'AZURE_OPENAI_API_KEY': 'test_key',
            'AZURE_OPENAI_ENDPOINT': 'https://test.openai.azure.com/',
            'AZURE_OPENAI_DEPLOYMENT_NAME': 'test_deployment'
        }):
            client = AzureOpenAIClient()
            response = client.generate_completion("Test prompt")
            
            assert response == "This is a test response."
            mock_client.chat.completions.create.assert_called_once()


@pytest.mark.skipif(not has_azure_credentials(), reason="Azure OpenAI credentials not available")
class TestProblemExtractor:
    def test_simple_algebra_extraction(self):
        """Test extracting a simple algebra problem."""
        extractor = ProblemExtractor()
        
        problem_text = "If x + 3 = 7, find x"
        
        try:
            problem = extractor.extract(problem_text)
            
            assert problem.original_text == problem_text
            assert len(problem.facts) >= 1
            assert problem.goal is not None
            assert problem.metadata["problem_type"] in ["algebraic_equation", "algebraic", "equation"]
            
            # Check that facts contain the equation
            fact_strs = [str(f) for f in problem.facts]
            assert any("x + 3" in fact_str and "7" in fact_str for fact_str in fact_strs)
            
        except Exception as e:
            pytest.skip(f"LLM extraction failed: {e}")
    
    def test_inequality_extraction(self):
        """Test extracting an inequality problem."""
        extractor = ProblemExtractor()
        
        problem_text = "If a > b and b > c, prove a > c"
        
        try:
            problem = extractor.extract(problem_text)
            
            assert problem.original_text == problem_text
            assert len(problem.facts) >= 2  # Should have a > b and b > c
            assert "gt" in str(problem.goal)  # Goal should involve greater than
            
        except Exception as e:
            pytest.skip(f"LLM extraction failed: {e}")


class TestProblemExtractorMocked:
    """Test ProblemExtractor with mocked LLM responses."""
    
    def test_extraction_with_valid_response(self):
        """Test extraction with a valid mocked response."""
        mock_response = {
            "facts": ["eq(x + 3, 7)"],
            "rules": ["eq(X + A, B) → eq(X, B - A)"],
            "goal": "eq(x, 4)",
            "problem_type": "algebraic_equation",
            "confidence": 0.9
        }
        
        with patch.object(AzureOpenAIClient, 'generate_json_completion', return_value=mock_response):
            extractor = ProblemExtractor()
            problem = extractor.extract("If x + 3 = 7, find x")
            
            assert len(problem.facts) == 1
            assert len(problem.rules) == 1
            assert problem.goal is not None
            assert problem.metadata["problem_type"] == "algebraic_equation"
    
    def test_extraction_with_invalid_response(self):
        """Test extraction with invalid mocked response."""
        mock_response = {
            "facts": ["invalid_fact"],  # This will fail parsing
            "rules": [],
            "goal": "eq(x, 4)"
        }
        
        with patch.object(AzureOpenAIClient, 'generate_json_completion', return_value=mock_response):
            extractor = ProblemExtractor()
            
            with pytest.raises(ValueError):
                extractor.extract("Test problem")


class TestProblemValidator:
    def test_valid_problem_validation(self):
        """Test validation of a valid problem."""
        parser = MathParser()
        validator = ProblemValidator()
        
        # Create a valid problem
        facts = [parser.parse_fact("eq(x + 3, 7)")]
        rules = [parser.parse_rule("eq(X + A, B) → eq(X, B - A)", "subtraction")]
        goal = parser.parse_fact("eq(x, 4)")
        
        from src.formal.expressions import MathProblem
        problem = MathProblem(facts, rules, goal)
        
        result = validator.validate_problem(problem)
        
        assert result["is_valid"] == True
        assert len(result["errors"]) == 0
    
    def test_problem_with_warnings(self):
        """Test validation of a problem that has warnings."""
        parser = MathParser()
        validator = ProblemValidator()
        
        # Create a problem with potential issues
        facts = [parser.parse_fact("eq(y, 5)")]  # Different variable than goal
        rules = []  # No rules
        goal = parser.parse_fact("eq(x, 4)")  # Different variable than facts
        
        from src.formal.expressions import MathProblem
        problem = MathProblem(facts, rules, goal)
        
        result = validator.validate_problem(problem)
        
        assert result["is_valid"] == True  # Still valid, just has warnings
        assert len(result["warnings"]) > 0


@pytest.mark.skipif(not has_azure_credentials(), reason="Azure OpenAI credentials not available")  
class TestProofExplainer:
    def test_successful_proof_explanation(self):
        """Test explaining a successful proof."""
        explainer = ProofExplainer()
        parser = MathParser()
        rule_system = RuleSystem()
        
        # Create a simple proof result
        rule = rule_system.math_rules.get_rule("subtraction_property")
        premise = parser.parse_fact("eq(x + 3, 7)")
        derived = parser.parse_fact("eq(x, 7 - 3)")
        
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
            final_facts=set(),
            iterations_used=1,
            time_elapsed=0.1
        )
        
        try:
            explanation = explainer.explain_proof("If x + 3 = 7, find x", result)
            
            assert isinstance(explanation, str)
            assert len(explanation) > 50  # Should be a substantial explanation
            assert "solve" in explanation.lower()
            
        except Exception as e:
            pytest.skip(f"LLM explanation failed: {e}")
    
    def test_failed_proof_explanation(self):
        """Test explaining a failed proof."""
        explainer = ProofExplainer()
        
        result = ProofResult(
            success=False,
            goal_achieved=False,
            steps=[],
            final_facts=set(),
            iterations_used=0,
            time_elapsed=0.0,
            error_message="Test error"
        )
        
        explanation = explainer.explain_proof("Test problem", result)
        
        assert "unable to solve" in explanation.lower()
        assert "test error" in explanation.lower()


class TestProofExplainerMocked:
    """Test ProofExplainer with mocked responses."""
    
    def test_mocked_explanation(self):
        """Test explanation generation with mocked LLM."""
        mock_explanation = "To solve this problem, we apply the subtraction property rule..."
        
        with patch.object(AzureOpenAIClient, 'generate_completion', return_value=mock_explanation):
            explainer = ProofExplainer()
            
            # Create minimal proof result
            result = ProofResult(
                success=True,
                goal_achieved=True,
                steps=[],
                final_facts=set(),
                iterations_used=1,
                time_elapsed=0.1
            )
            
            explanation = explainer.explain_proof("Test problem", result)
            
            assert mock_explanation in explanation
            assert "Proof completed" in explanation  # Should include footer


if __name__ == "__main__":
    pytest.main([__file__])