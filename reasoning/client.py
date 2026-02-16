"""LLM client for structured reasoning with Google Gemini API.

Handles API calls, retries, validation, and response parsing.
"""
import json
import time
from typing import Optional

from google import genai
from google.genai import types
from pydantic import ValidationError

from config import GrintaConfig, get_config
from reasoning.output_schema import ExplanationResponse, EXPLANATION_JSON_SCHEMA
from reasoning.prompts import SYSTEM_PROMPT


class ReasoningClient:
    """Client for making LLM reasoning calls with structured output.
    
    Handles:
    - Google Gemini API calls with JSON mode
    - Response validation against output schema
    - Retry logic for transient failures
    - Token usage tracking
    """
    
    def __init__(self, config: Optional[GrintaConfig] = None):
        """Initialize the reasoning client.
        
        Args:
            config: Optional config. If not provided, loads from environment.
        """
        self.config = config or get_config()
        
        # Validate API key is configured
        self.config.require_reasoning()
        
        # Create the client
        self.client = genai.Client(api_key=self.config.api_key)
        
        self.total_tokens_used = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
    
    def generate_explanation(
        self,
        user_prompt: str,
        system_prompt: Optional[str] = None
    ) -> ExplanationResponse:
        """Generate a structured explanation using the LLM.
        
        Args:
            user_prompt: The user prompt with metrics and question
            system_prompt: Optional system prompt override (uses default if not provided)
            
        Returns:
            Validated ExplanationResponse
            
        Raises:
            Exception: If API call fails after retries
            ValidationError: If response doesn't match schema
        """
        system_prompt = system_prompt or SYSTEM_PROMPT
        
        # Attempt with retries
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                response = self._call_api(system_prompt, user_prompt)
                
                # Parse and validate response
                return self._parse_response(response)
                
            except Exception as e:
                last_error = e
                if attempt < self.config.max_retries - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    raise
        
        # Should not reach here, but just in case
        if last_error:
            raise last_error
        raise RuntimeError("Failed to generate explanation after retries")
    
    def _call_api(self, system_prompt: str, user_prompt: str):
        """Make the actual API call to Gemini.
        
        Args:
            system_prompt: System instructions
            user_prompt: User prompt with metrics
            
        Returns:
            Gemini generate content response
        """
        # Combine system prompt and user prompt
        full_prompt = f"{system_prompt}\n\n{user_prompt}\n\nIMPORTANT: Return ONLY valid JSON matching the required schema. No markdown, no code blocks, just pure JSON."
        
        # Generate without schema first (more reliable)
        response = self.client.models.generate_content(
            model=self.config.model,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_tokens,
                response_mime_type="application/json",
            )
        )
        
        return response
    
    def _parse_response(self, response) -> ExplanationResponse:
        """Parse and validate the LLM response.
        
        Args:
            response: Gemini generate content response
            
        Returns:
            Validated ExplanationResponse
            
        Raises:
            ValidationError: If response doesn't match schema
            ValueError: If response is malformed
        """
        # Extract content
        if not response.text:
            raise ValueError("Empty content in API response")
        
        content = response.text.strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        elif content.startswith("```"):
            content = content.replace("```", "").strip()
        
        # Try to parse JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            # Try to fix common JSON issues
            print(f"JSON parse error: {e}")
            print(f"Content preview (first 1000 chars):\n{content[:1000]}")
            
            # Attempt to repair: replace literal newlines in strings
            import re
            # This is a simple attempt - won't handle all cases
            try:
                # Replace unescaped newlines within quoted strings
                fixed_content = content.replace('\n', '\\n').replace('\r', '\\r')
                # Try again
                data = json.loads(fixed_content)
                print("Successfully repaired JSON")
            except json.JSONDecodeError as e2:
                raise ValueError(f"Failed to parse JSON even after repair attempt. Original error: {e}. Repair error: {e2}. Check terminal for content preview.")
        
        # Validate against schema
        try:
            return ExplanationResponse(**data)
        except ValidationError as e:
            print(f"Validation error: {e}")
            raise ValidationError(f"Response validation failed: {e}")
    
    def get_token_usage(self) -> dict:
        """Get total token usage statistics.
        
        Returns:
            Dict with token usage counts
        """
        return {
            "total_tokens": self.total_tokens_used,
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens
        }
    
    def reset_token_usage(self):
        """Reset token usage counters."""
        self.total_tokens_used = 0
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0


def create_reasoning_client(config: Optional[GrintaConfig] = None) -> ReasoningClient:
    """Factory function to create a reasoning client.
    
    Args:
        config: Optional configuration. If not provided, loads from environment.
        
    Returns:
        ReasoningClient instance
    """
    return ReasoningClient(config=config)
