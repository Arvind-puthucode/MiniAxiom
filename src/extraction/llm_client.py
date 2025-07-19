"""
Azure OpenAI client for LLM integration.

This module provides the interface to Azure OpenAI API for problem extraction
and proof explanation generation.
"""
import os
import json
from typing import Dict, Any
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AzureOpenAIClient:
    """Client for Azure OpenAI API."""
    
    def __init__(self):
        """Initialize Azure OpenAI client with environment variables."""
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT") 
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        if not all([self.api_key, self.endpoint, self.deployment_name]):
            raise ValueError(
                "Missing Azure OpenAI configuration. Please set AZURE_OPENAI_API_KEY, "
                "AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT_NAME in your .env file"
            )
        
        # Initialize OpenAI client
        self.client = openai.AzureOpenAI(
            api_key=self.api_key,
            api_version=self.api_version,
            azure_endpoint=self.endpoint
        )
    
    def generate_completion(self, prompt: str, max_tokens: int = 1000, 
                          temperature: float = 0.1) -> str:
        """
        Generate a completion using Azure OpenAI.
        
        Args:
            prompt: The input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (lower = more deterministic)
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a mathematical reasoning expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise RuntimeError(f"Azure OpenAI API error: {str(e)}")
    
    def generate_json_completion(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """
        Generate a JSON completion using Azure OpenAI.
        
        Args:
            prompt: The input prompt requesting JSON output
            max_tokens: Maximum tokens to generate
            
        Returns:
            Parsed JSON response as dictionary
        """
        try:
            # Add JSON formatting instruction
            json_prompt = f"{prompt}\n\nPlease respond with valid JSON only, no additional text."
            
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": "You are a mathematical reasoning expert. Always respond with valid JSON."},
                    {"role": "user", "content": json_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.1,  # Lower temperature for more consistent JSON
                response_format={"type": "json_object"}  # Force JSON output
            )
            
            content = response.choices[0].message.content.strip()
            return json.loads(content)
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Azure OpenAI API error: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test the Azure OpenAI connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = self.generate_completion("Hello, this is a test.", max_tokens=10)
            return len(response) > 0
        except Exception:
            return False