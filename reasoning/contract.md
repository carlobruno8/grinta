# Reasoning Module

The reasoning module bridges computed metrics and LLM-based explanations for football matches.

## Vision

Generate **grounded, auditable explanations** using only provided metrics. No hallucinations, no external knowledge.

## Core Principles

1. **Evidence > Fluency** - All claims must map to computed data
2. **No hallucinated metrics** - Only use metrics from the features module
3. **Explicit uncertainty** - State confidence levels and limitations
4. **Structured output** - Validated JSON responses
5. **Auditable reasoning** - Every claim traces back to evidence

---

## Architecture

```
┌─────────────┐
│  Features   │ (compute team metrics)
│   Module    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Input     │ (ReasoningInput with TeamMetrics)
│   Schema    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Prompts    │ (system prompt + user prompt builder)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  LLM Client │ (Google Gemini API with JSON mode)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Output    │ (ExplanationResponse validated)
│   Schema    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ Streamlit   │ (display to user)
│     App     │
└─────────────┘
```

---

## Quick Start

### Installation

Set your Google AI API key:

```bash
export GOOGLE_API_KEY="your-google-api-key"
```

Optional configuration:

```bash
export GRINTA_LLM_MODEL="gemini-1.5-flash"  # Default model
export GRINTA_LLM_TEMPERATURE=0.0           # Deterministic
```

### Basic Usage

```python
from reasoning import generate_explanation

# Generate explanation for full match
response = generate_explanation(
    match_id=123456,
    question="Why did Liverpool lose control after halftime?"
)

print(response.explanation.summary)

# Access structured claims
for claim in response.explanation.claims:
    print(f"Claim: {claim.statement}")
    print(f"Confidence: {claim.confidence}")
    for evidence in claim.supporting_evidence:
        print(f"  - {evidence.metric_name}: {evidence.value}")
```

### Time Windows

Analyze specific time periods:

```python
# Last 10 minutes
response = generate_explanation(
    match_id=123456,
    question="Why did Team A concede late?",
    time_filter="last_10_min"
)

# Specific period
response = generate_explanation(
    match_id=123456,
    question="How did Team B perform in the second half?",
    time_filter="period_2"
)

# First 15 minutes
response = generate_explanation(
    match_id=123456,
    question="Did Team A start strong?",
    time_filter="first_15_min"
)
```

### Convenience Function

For simple use cases:

```python
from reasoning import explain_match

# Returns dict instead of ExplanationResponse
explanation_dict = explain_match(
    match_id=123456,
    question="Why did Arsenal dominate possession?"
)
```

---

## Module Structure

### Core Components

- **`input_schema.py`** - Pydantic models for input data
  - `TeamMetrics`: Possession, shots, territory metrics
  - `MatchContext`: Match metadata
  - `TimeWindowContext`: Time filter info
  - `ReasoningInput`: Complete input package

- **`output_schema.py`** - Pydantic models for LLM output
  - `Evidence`: Single piece of evidence
  - `Claim`: Factual claim with supporting evidence
  - `Explanation`: Complete explanation with confidence
  - `ExplanationResponse`: Top-level response

- **`prompts.py`** - System and user prompt templates
  - `SYSTEM_PROMPT`: Constraints and instructions for LLM
  - `build_user_prompt()`: Format metrics into user prompt

- **`client.py`** - Google Gemini API wrapper
  - `ReasoningClient`: Handles API calls, retries, validation
  - Token tracking and error handling

- **`builder.py`** - High-level orchestrator
  - `generate_explanation()`: Main entry point
  - `compute_team_metrics()`: Compute metrics from events
  - `apply_time_filter()`: Filter events by time window

- **`config.py`** - Configuration management
  - `ReasoningConfig`: API keys, model selection, parameters
  - Environment variable loading

---

## Workflow

### 1. Load Match Events

```python
from features.reader import load_match_events

events_df = load_match_events(match_id=123456)
```

### 2. Apply Time Filter (Optional)

```python
from reasoning.builder import apply_time_filter

filtered_df, time_context = apply_time_filter(
    events_df, 
    time_filter="last_10_min"
)
```

### 3. Compute Team Metrics

```python
from reasoning.builder import compute_team_metrics

metrics = compute_team_metrics(
    events_df=filtered_df,
    team_id=217,
    team_name="Liverpool"
)
```

### 4. Build Reasoning Input

```python
from reasoning.input_schema import ReasoningInput, MatchContext

reasoning_input = ReasoningInput(
    match_context=MatchContext(
        match_id=123456,
        home_team="Liverpool",
        away_team="Arsenal"
    ),
    time_window=time_context,
    team_metrics=[metrics_team_a, metrics_team_b],
    question="Why did Liverpool concede late?"
)
```

### 5. Generate Explanation

```python
from reasoning.prompts import build_user_prompt
from reasoning.client import create_reasoning_client

user_prompt = build_user_prompt(reasoning_input)
client = create_reasoning_client()
response = client.generate_explanation(user_prompt)
```

### 6. Use the Explanation

```python
# Summary
print(response.explanation.summary)

# Claims with evidence
for claim in response.explanation.claims:
    print(claim.statement)
    for evidence in claim.supporting_evidence:
        print(f"  {evidence.metric_name}: {evidence.value}")

# Confidence and caveats
print(f"Confidence: {response.explanation.overall_confidence}")
for caveat in response.explanation.caveats:
    print(f"  - {caveat}")
```

---

## Integration with Features Module

The reasoning module consumes metrics from the features module:

```python
# From features module
from features.possession import possession_share_from_passes
from features.shots import shot_counts_by_team, goals_by_team
from features.territory import average_position_by_team

# Metrics are automatically computed in builder.py
metrics = compute_team_metrics(events_df, team_id, team_name)
```

### Available Metrics

**Possession:**
- `possession_share` (0-1)
- `pass_count`
- `successful_passes`
- `pass_completion_rate` (0-1)

**Shots:**
- `shot_count`
- `shots_on_target`
- `goals`

**Territory:**
- `avg_position_x` (0-120 scale)
- `avg_position_y` (0-80 scale)
- `final_third_entries`

---

## Testing

### Unit Tests

Test schemas and prompt generation:

```bash
pytest tests/test_reasoning.py -v -k "test_input_schema or test_output_schema"
```

### Integration Tests

Test with mocked LLM responses:

```bash
pytest tests/test_reasoning.py -v -k "test_client_mock"
```

### End-to-End Tests

Test with real API calls (requires `GOOGLE_API_KEY`):

```bash
pytest tests/test_reasoning.py -v -k "test_e2e"
```

---

## Error Handling

The reasoning module handles various error scenarios:

### API Errors

- **ResourceExhausted**: Rate limit - automatic retry with exponential backoff
- **ServiceUnavailable**: Service unavailable - retry up to `max_retries` times
- **GoogleAPIError**: Client errors (4xx) fail immediately, server errors retry

### Validation Errors

- **Invalid Input**: Pydantic validation catches malformed inputs
- **Invalid Output**: LLM responses validated against schema
- **Missing Data**: Graceful handling of missing metrics (None values)

### Example Error Handling

```python
from reasoning import generate_explanation
from google.api_core import exceptions as google_exceptions
from pydantic import ValidationError

try:
    response = generate_explanation(
        match_id=123456,
        question="Why did Team A win?"
    )
except FileNotFoundError:
    print("Match events file not found")
except google_exceptions.GoogleAPIError as e:
    print(f"Google AI API error: {e}")
except ValidationError as e:
    print(f"Response validation failed: {e}")
```

---

## Token Usage Tracking

Track LLM costs:

```python
from reasoning.client import create_reasoning_client

client = create_reasoning_client()

# Generate explanations
response1 = client.generate_explanation(prompt1)
response2 = client.generate_explanation(prompt2)

# Check usage
usage = client.get_token_usage()
print(f"Total tokens: {usage['total_tokens']}")
print(f"Prompt tokens: {usage['prompt_tokens']}")
print(f"Completion tokens: {usage['completion_tokens']}")

# Reset counters
client.reset_token_usage()
```

---

## Advanced Configuration

### Custom Model

```python
from reasoning import ReasoningConfig, generate_explanation

config = ReasoningConfig(
    api_key="sk-...",
    model="gpt-4o",  # Use more capable model
    temperature=0.1,
    max_tokens=3000
)

response = generate_explanation(
    match_id=123456,
    question="Explain the match dynamics",
    reasoning_config=config
)
```

### Reuse Client

For multiple queries, reuse the client:

```python
from reasoning.client import create_reasoning_client
from reasoning.builder import generate_explanation

client = create_reasoning_client()

# Multiple explanations with same client
for question in questions:
    response = generate_explanation(
        match_id=123456,
        question=question,
        client=client  # Reuse client
    )
```

---

## Limitations (Phase 1)

Current scope is **team-level explanations only**:

✅ Supported:
- Team possession metrics
- Team shot statistics
- Team territorial metrics
- Time-windowed analysis

❌ Not yet supported:
- Player-level analysis
- Tactical formation detection
- Pass networks
- Defensive actions (tackles, interceptions)
- Set piece analysis

---

## Future Enhancements

Post Phase 1 roadmap:

- **Multi-turn conversations**: Follow-up questions with context
- **Player-level reasoning**: Individual player performance
- **Comparative analysis**: Team A vs Team B side-by-side
- **Confidence calibration**: Improve confidence scoring
- **Tactical pattern detection**: Formation and style recognition
- **Interactive explanations**: Drill down into specific claims

---

## Example Outputs

### Example 1: Late Goal Conceded

**Question**: "Why did Liverpool concede in the last 10 minutes?"

**Response Summary**:
"In the last 10 minutes, Liverpool's average position dropped to 48.5 (from 58.2 full-match), while Arsenal increased pressure with 12 final third entries and 4 shots. However, without defensive action data, we cannot determine if this was tactical or forced."

**Claims**:
1. Liverpool defended deeper in final 10 minutes (confidence: high)
   - avg_position_x: 48.5 vs 58.2
   
2. Arsenal increased attacking pressure (confidence: high)
   - final_third_entries: 12
   - shot_count: 4

**Caveats**:
- No data on defensive actions (blocks, tackles)
- Cannot determine if positional change was tactical

### Example 2: Possession Dominance

**Question**: "Why did Manchester City dominate possession?"

**Response Summary**:
"Manchester City had 68% possession (0.68) with 612 completed passes compared to 287 for the opponent. Their average position was higher (61.2 vs 42.8), indicating territorial control. However, possession alone doesn't explain match outcome without shot data."

**Claims**:
1. City controlled the ball significantly (confidence: high)
   - possession_share: 0.68
   - successful_passes: 612 vs 287
   
2. City maintained higher field position (confidence: high)
   - avg_position_x: 61.2 vs 42.8

**Caveats**:
- Possession doesn't guarantee scoring
- Need shot quality data for complete picture

---

## Support

For issues or questions:
1. Check test files: `tests/test_reasoning.py`
2. Review examples in this contract
3. Consult system prompt: `reasoning/prompts.py`

---

## Philosophy

The LLM is **not allowed to**:
- Fetch data
- Compute metrics
- Use external football knowledge
- Make predictions

It **only reasons** over structured inputs.

This enforces **disciplined, explainable AI** for football analytics.
