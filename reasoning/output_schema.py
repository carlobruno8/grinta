"""Output schema for LLM reasoning.

Defines the structured explanation format the LLM must return.
All explanations must be grounded in provided evidence.
"""
from typing import Union, Literal
from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """A single piece of evidence from the provided metrics.
    
    Evidence must reference a metric that was provided in the input.
    """
    metric_name: str = Field(
        description="Name of the metric (must match input schema field names)"
    )
    value: Union[float, int, str] = Field(
        description="The value of the metric"
    )
    interpretation: str = Field(
        description="Brief interpretation of what this metric means in context (1-2 sentences)"
    )


class Claim(BaseModel):
    """A factual claim supported by evidence.
    
    Claims must be directly supported by the evidence list.
    No claims should be made without corresponding evidence.
    """
    statement: str = Field(
        description="The factual statement being made"
    )
    supporting_evidence: list[Evidence] = Field(
        min_length=1,
        description="List of evidence items that support this claim"
    )
    confidence: Literal["high", "medium", "low"] = Field(
        description="Confidence level: high (direct metric support), medium (inferred from multiple metrics), low (limited data)"
    )


class Explanation(BaseModel):
    """Complete explanation with claims, confidence, and caveats.
    
    This is the main explanation structure returned by the LLM.
    """
    claims: list[Claim] = Field(
        min_length=1,
        description="List of factual claims that answer the question"
    )
    overall_confidence: Literal["high", "medium", "low"] = Field(
        description="Overall confidence in the explanation based on data quality and completeness"
    )
    caveats: list[str] = Field(
        default_factory=list,
        description="Important limitations, missing context, or factors not captured in the data"
    )
    summary: str = Field(
        description="2-3 sentence summary of the explanation, written for a football fan"
    )


class ExplanationResponse(BaseModel):
    """Top-level response wrapper for LLM output.
    
    This is what the LLM must return, validated against this schema.
    """
    explanation: Explanation
    
    # Metadata about the reasoning process
    question_understood: bool = Field(
        True,
        description="Whether the LLM understood the question (false if ambiguous or unanswerable)"
    )
    clarification_needed: str | None = Field(
        None,
        description="If question is unclear, what clarification is needed"
    )
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return self.model_dump()
    
    def to_json(self, **kwargs) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(**kwargs)


# JSON schema for Gemini structured output
EXPLANATION_JSON_SCHEMA = {
    "name": "explanation_response",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "explanation": {
                "type": "object",
                "properties": {
                    "claims": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "statement": {"type": "string"},
                                "supporting_evidence": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "metric_name": {"type": "string"},
                                            "value": {"type": "string"},
                                            "interpretation": {"type": "string"}
                                        },
                                        "required": ["metric_name", "value", "interpretation"]
                                    }
                                },
                                "confidence": {
                                    "type": "string",
                                    "enum": ["high", "medium", "low"]
                                }
                            },
                            "required": ["statement", "supporting_evidence", "confidence"]
                        }
                    },
                    "overall_confidence": {
                        "type": "string",
                        "enum": ["high", "medium", "low"]
                    },
                    "caveats": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "summary": {"type": "string"}
                },
                "required": ["claims", "overall_confidence", "caveats", "summary"]
            },
            "question_understood": {"type": "boolean"},
            "clarification_needed": {"type": "string", "nullable": True}
        },
        "required": ["explanation", "question_understood"]
    }
}
