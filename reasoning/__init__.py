"""Reasoning module - Evidence-based football match explanations.

This module provides structured, LLM-powered explanations for football matches
using team-level metrics. All explanations are grounded in computed data with
no hallucinated metrics.

Main entry points:
    - generate_explanation(): Generate structured explanation for a match question
    - explain_match(): Convenience function returning dict
    
Example:
    from reasoning import generate_explanation
    
    response = generate_explanation(
        match_id=123456,
        question="Why did Team A concede in the last 10 minutes?",
        time_filter="last_10_min"
    )
    
    print(response.explanation.summary)
"""

from config import GrintaConfig, get_config
from reasoning.builder import generate_explanation, explain_match
from reasoning.input_schema import ReasoningInput, TeamMetrics, MatchContext, TimeWindowContext
from reasoning.output_schema import ExplanationResponse, Explanation, Claim, Evidence
from reasoning.client import ReasoningClient, create_reasoning_client

__all__ = [
    # Main functions
    "generate_explanation",
    "explain_match",
    
    # Input schemas
    "ReasoningInput",
    "TeamMetrics", 
    "MatchContext",
    "TimeWindowContext",
    
    # Output schemas
    "ExplanationResponse",
    "Explanation",
    "Claim",
    "Evidence",
    
    # Client
    "ReasoningClient",
    "create_reasoning_client",
    
    # Config
    "GrintaConfig",
    "get_config",
]
