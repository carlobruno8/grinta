"""Tests for the reasoning module.

Tests cover:
- Input/output schema validation
- Prompt generation
- Client integration (mocked)
- End-to-end pipeline (requires API key)
"""
import json
import pytest
from unittest.mock import Mock, patch
import pandas as pd

from reasoning.input_schema import (
    TeamMetrics, 
    MatchContext, 
    TimeWindowContext, 
    ReasoningInput
)
from reasoning.output_schema import (
    Evidence, 
    Claim, 
    Explanation, 
    ExplanationResponse
)
from reasoning.prompts import build_user_prompt, SYSTEM_PROMPT
from config import GrintaConfig
from reasoning.client import ReasoningClient
from reasoning.builder import (
    compute_team_metrics,
    apply_time_filter,
    extract_teams_from_events
)


# ============================================================================
# Input Schema Tests
# ============================================================================

def test_team_metrics_validation():
    """Test TeamMetrics validation and derived fields."""
    metrics = TeamMetrics(
        team_id=217,
        team_name="Liverpool",
        pass_count=450,
        successful_passes=400,
        possession_share=0.65
    )
    
    assert metrics.team_id == 217
    assert metrics.team_name == "Liverpool"
    assert metrics.pass_completion_rate == pytest.approx(400 / 450)
    

def test_team_metrics_optional_fields():
    """Test that all metric fields are optional except team_id and team_name."""
    metrics = TeamMetrics(
        team_id=1,
        team_name="Test Team"
    )
    
    assert metrics.possession_share is None
    assert metrics.shot_count is None
    assert metrics.goals is None


def test_reasoning_input_creation():
    """Test creating a complete ReasoningInput."""
    team1 = TeamMetrics(team_id=1, team_name="Team A", possession_share=0.6)
    team2 = TeamMetrics(team_id=2, team_name="Team B", possession_share=0.4)
    
    match_ctx = MatchContext(
        match_id=123,
        home_team="Team A",
        away_team="Team B"
    )
    
    time_ctx = TimeWindowContext(description="Full Match")
    
    reasoning_input = ReasoningInput(
        match_context=match_ctx,
        time_window=time_ctx,
        team_metrics=[team1, team2],
        question="Why did Team A win?"
    )
    
    assert reasoning_input.match_context.match_id == 123
    assert len(reasoning_input.team_metrics) == 2
    assert reasoning_input.question == "Why did Team A win?"


def test_reasoning_input_get_team():
    """Test getting team by name and ID."""
    team1 = TeamMetrics(team_id=1, team_name="Liverpool")
    team2 = TeamMetrics(team_id=2, team_name="Arsenal")
    
    reasoning_input = ReasoningInput(
        match_context=MatchContext(match_id=1, home_team="Liverpool", away_team="Arsenal"),
        time_window=TimeWindowContext(description="Full"),
        team_metrics=[team1, team2],
        question="Test?"
    )
    
    # Get by name
    liverpool = reasoning_input.get_team_by_name("Liverpool")
    assert liverpool.team_id == 1
    
    # Get by ID
    arsenal = reasoning_input.get_team_by_id(2)
    assert arsenal.team_name == "Arsenal"
    
    # Not found
    assert reasoning_input.get_team_by_name("Chelsea") is None


# ============================================================================
# Output Schema Tests
# ============================================================================

def test_evidence_creation():
    """Test creating Evidence objects."""
    evidence = Evidence(
        metric_name="possession_share",
        value=0.65,
        interpretation="Team had 65% possession"
    )
    
    assert evidence.metric_name == "possession_share"
    assert evidence.value == 0.65


def test_claim_creation():
    """Test creating Claim with evidence."""
    evidence = Evidence(
        metric_name="shot_count",
        value=15,
        interpretation="Team took 15 shots"
    )
    
    claim = Claim(
        statement="Team dominated attacking play",
        supporting_evidence=[evidence],
        confidence="high"
    )
    
    assert claim.statement == "Team dominated attacking play"
    assert len(claim.supporting_evidence) == 1
    assert claim.confidence == "high"


def test_explanation_response():
    """Test creating complete ExplanationResponse."""
    evidence = Evidence(
        metric_name="goals",
        value=3,
        interpretation="Team scored 3 goals"
    )
    
    claim = Claim(
        statement="Team won comfortably",
        supporting_evidence=[evidence],
        confidence="high"
    )
    
    explanation = Explanation(
        claims=[claim],
        overall_confidence="high",
        caveats=["Limited to scoring data"],
        summary="Team won 3-0 with dominant performance"
    )
    
    response = ExplanationResponse(
        explanation=explanation,
        question_understood=True
    )
    
    assert response.explanation.overall_confidence == "high"
    assert len(response.explanation.claims) == 1
    assert response.question_understood is True


def test_explanation_response_serialization():
    """Test converting ExplanationResponse to dict/JSON."""
    evidence = Evidence(
        metric_name="goals",
        value=2,
        interpretation="2 goals scored"
    )
    
    claim = Claim(
        statement="Team won",
        supporting_evidence=[evidence],
        confidence="high"
    )
    
    explanation = Explanation(
        claims=[claim],
        overall_confidence="high",
        caveats=[],
        summary="Team won 2-0"
    )
    
    response = ExplanationResponse(
        explanation=explanation,
        question_understood=True
    )
    
    # To dict
    data = response.to_dict()
    assert isinstance(data, dict)
    assert "explanation" in data
    
    # To JSON
    json_str = response.to_json()
    assert isinstance(json_str, str)
    parsed = json.loads(json_str)
    assert parsed["question_understood"] is True


# ============================================================================
# Prompt Generation Tests
# ============================================================================

def test_build_user_prompt():
    """Test building user prompt from ReasoningInput."""
    team1 = TeamMetrics(
        team_id=1,
        team_name="Liverpool",
        possession_share=0.65,
        shot_count=15,
        goals=2
    )
    
    team2 = TeamMetrics(
        team_id=2,
        team_name="Arsenal",
        possession_share=0.35,
        shot_count=8,
        goals=1
    )
    
    reasoning_input = ReasoningInput(
        match_context=MatchContext(
            match_id=123,
            home_team="Liverpool",
            away_team="Arsenal",
            competition="Premier League"
        ),
        time_window=TimeWindowContext(description="Full Match"),
        team_metrics=[team1, team2],
        question="Why did Liverpool win?"
    )
    
    prompt = build_user_prompt(reasoning_input)
    
    # Check prompt contains key information
    assert "Liverpool" in prompt
    assert "Arsenal" in prompt
    assert "123" in prompt
    assert "Premier League" in prompt
    assert "possession_share: 0.650" in prompt
    assert "shot_count: 15" in prompt
    assert "Why did Liverpool win?" in prompt


def test_system_prompt_exists():
    """Test that system prompt is defined and non-empty."""
    assert SYSTEM_PROMPT
    assert len(SYSTEM_PROMPT) > 100
    assert "evidence" in SYSTEM_PROMPT.lower()
    assert "metric" in SYSTEM_PROMPT.lower()


# ============================================================================
# Builder Tests
# ============================================================================

def test_extract_teams_from_events():
    """Test extracting team info from events DataFrame."""
    events_df = pd.DataFrame({
        'team_id': [1, 1, 2, 2],
        'team_name': ['Liverpool', 'Liverpool', 'Arsenal', 'Arsenal'],
        'type_name': ['Pass', 'Shot', 'Pass', 'Shot']
    })
    
    teams = extract_teams_from_events(events_df)
    
    assert len(teams) == 2
    assert (1, 'Liverpool') in teams
    assert (2, 'Arsenal') in teams


def test_apply_time_filter_full_match():
    """Test time filter with no filter (full match)."""
    events_df = pd.DataFrame({
        'period': [1, 1, 2, 2],
        'timestamp': ['00:10:00', '00:20:00', '00:05:00', '00:15:00']
    })
    
    filtered_df, time_ctx = apply_time_filter(events_df, time_filter=None)
    
    assert len(filtered_df) == 4
    assert time_ctx.description == "Full Match"


def test_apply_time_filter_period():
    """Test filtering by period."""
    events_df = pd.DataFrame({
        'period': [1, 1, 2, 2],
        'timestamp': ['00:10:00', '00:20:00', '00:05:00', '00:15:00']
    })
    
    filtered_df, time_ctx = apply_time_filter(events_df, time_filter="period_2")
    
    assert len(filtered_df) == 2
    assert all(filtered_df['period'] == 2)
    assert time_ctx.description == "Period 2"
    assert time_ctx.period == 2


def test_compute_team_metrics_basic():
    """Test computing team metrics from events."""
    events_df = pd.DataFrame({
        'team_id': [1, 1, 1, 2, 2],
        'team_name': ['Liverpool', 'Liverpool', 'Liverpool', 'Arsenal', 'Arsenal'],
        'type_name': ['Pass', 'Pass', 'Shot', 'Pass', 'Shot'],
        'shot_outcome': [None, None, 'Goal', None, 'Saved'],
        'x': [50, 60, 90, 40, 85],
        'y': [40, 40, 40, 40, 40]
    })
    
    metrics = compute_team_metrics(events_df, team_id=1, team_name="Liverpool")
    
    assert metrics.team_id == 1
    assert metrics.team_name == "Liverpool"
    assert metrics.pass_count == 2
    assert metrics.shot_count == 1
    assert metrics.goals == 1


# ============================================================================
# Client Tests (Mocked)
# ============================================================================

@patch('reasoning.client.genai')
def test_reasoning_client_initialization(mock_genai):
    """Test ReasoningClient initialization."""
    config = GrintaConfig(
        api_key="test-api-key",
        model="gemini-1.5-flash"
    )
    
    client = ReasoningClient(config)
    
    assert client.config.api_key == "test-api-key"
    assert client.config.model == "gemini-1.5-flash"
    assert client.total_tokens_used == 0


@patch('reasoning.client.genai')
def test_reasoning_client_successful_call(mock_genai):
    """Test successful LLM call with mocked response."""
    config = GrintaConfig(api_key="test-api-key")
    
    # Mock response
    mock_response = Mock()
    mock_response.candidates = [Mock()]
    mock_response.text = json.dumps({
        "explanation": {
            "claims": [{
                "statement": "Test claim",
                "supporting_evidence": [{
                    "metric_name": "test_metric",
                    "value": 1,
                    "interpretation": "Test"
                }],
                "confidence": "high"
            }],
            "overall_confidence": "high",
            "caveats": [],
            "summary": "Test summary"
        },
        "question_understood": True,
        "clarification_needed": None
    })
    mock_response.usage_metadata = Mock()
    mock_response.usage_metadata.total_token_count = 100
    mock_response.usage_metadata.prompt_token_count = 50
    mock_response.usage_metadata.candidates_token_count = 50
    
    mock_model = Mock()
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model
    
    client = ReasoningClient(config)
    response = client.generate_explanation("Test prompt")
    
    assert isinstance(response, ExplanationResponse)
    assert response.question_understood is True
    assert client.total_tokens_used == 100


# ============================================================================
# Integration Tests (require GOOGLE_API_KEY)
# ============================================================================

def test_e2e_explanation_generation(request):
    """End-to-end test with real API call (requires API key).
    
    Run with: pytest tests/test_reasoning.py -v -k test_e2e --run-integration
    """
    import os
    
    # Skip if --run-integration not passed or no API key
    if not request.config.getoption("--run-integration", default=False):
        pytest.skip("Integration tests require --run-integration flag")
    
    if not os.getenv("GOOGLE_API_KEY"):
        pytest.skip("GOOGLE_API_KEY not set")
    
    # Create sample events
    events_df = pd.DataFrame({
        'team_id': [1, 1, 1, 2, 2],
        'team_name': ['Liverpool', 'Liverpool', 'Liverpool', 'Arsenal', 'Arsenal'],
        'type_name': ['Pass', 'Pass', 'Shot', 'Pass', 'Shot'],
        'shot_outcome': [None, None, 'Goal', None, 'Saved'],
        'x': [50, 60, 90, 40, 85],
        'y': [40, 40, 40, 40, 40],
        'period': [1, 1, 1, 1, 1],
        'timestamp': ['00:10:00', '00:20:00', '00:30:00', '00:15:00', '00:25:00']
    })
    
    # This would require mocking load_match_events or having test data
    # For now, just test the client directly
    from reasoning.client import create_reasoning_client
    from reasoning.prompts import build_user_prompt
    from reasoning.input_schema import ReasoningInput, MatchContext, TimeWindowContext, TeamMetrics
    
    team1 = TeamMetrics(
        team_id=1,
        team_name="Liverpool",
        possession_share=0.6,
        shot_count=10,
        goals=2
    )
    
    team2 = TeamMetrics(
        team_id=2,
        team_name="Arsenal",
        possession_share=0.4,
        shot_count=5,
        goals=1
    )
    
    reasoning_input = ReasoningInput(
        match_context=MatchContext(match_id=1, home_team="Liverpool", away_team="Arsenal"),
        time_window=TimeWindowContext(description="Full Match"),
        team_metrics=[team1, team2],
        question="Why did Liverpool win?"
    )
    
    user_prompt = build_user_prompt(reasoning_input)
    client = create_reasoning_client()
    
    response = client.generate_explanation(user_prompt)
    
    assert isinstance(response, ExplanationResponse)
    assert response.question_understood is True
    assert len(response.explanation.claims) > 0
    assert response.explanation.summary


def pytest_addoption(parser):
    """Add custom pytest command line options."""
    parser.addoption(
        "--run-integration",
        action="store_true",
        default=False,
        help="Run integration tests that require API keys"
    )
