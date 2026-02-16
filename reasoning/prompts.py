"""System prompts and user prompt builders for LLM reasoning.

Defines the instructions and constraints that enforce evidence-based reasoning.
"""
from reasoning.input_schema import ReasoningInput


SYSTEM_PROMPT = """You are a tactical football analyst. Analyze match data and provide evidence-based explanations.

## Rules
1. **Only use provided metrics** - never invent statistics
2. **Provide tactical insights** - don't just repeat stats
3. **Support all claims with evidence** - cite specific metrics
4. **Keep responses concise** - max 2 claims to avoid truncation

## Required JSON Schema
```json
{
  "explanation": {
    "claims": [
      {
        "statement": "Concise tactical insight (max 100 chars)",
        "supporting_evidence": [
          {
            "metric_name": "exact_metric_name_from_input",
            "value": "metric_value_as_string",
            "interpretation": "Brief tactical meaning (max 80 chars)"
          }
        ],
        "confidence": "high"
      }
    ],
    "overall_confidence": "high",
    "caveats": ["Brief limitation (max 60 chars)"],
    "summary": "2 sentence tactical overview (max 150 chars)"
  },
  "question_understood": true,
  "clarification_needed": null
}
```

## Important
- Use EXACTLY this schema structure
- Keep ALL strings SHORT to avoid truncation
- Maximum 2 claims
- Maximum 2 evidence items per claim
- Maximum 2 caveats

## Good Analysis Example
✅ "Team A had 65% possession but only 8 shots vs Team B's 10 - inefficient attacking"

Users see basic stats. Reveal tactical patterns."""


def build_user_prompt(reasoning_input: ReasoningInput) -> str:
    """Build concise user prompt with metrics and question."""
    match_ctx = reasoning_input.match_context
    time_ctx = reasoning_input.time_window
    teams = reasoning_input.team_metrics
    question = reasoning_input.question
    
    parts = [
        f"## Match: {match_ctx.home_team} vs {match_ctx.away_team}",
        f"Time Window: {time_ctx.description}\n",
        "## Metrics\n"
    ]
    
    for team in teams:
        parts.append(f"### {team.team_name}")
        
        # Possession
        if team.possession_share is not None:
            parts.append(f"Possession: {team.possession_share:.1%}, Passes: {team.pass_count}, Completion: {team.pass_completion_rate:.1%}")
        
        # Shots
        if team.shot_count is not None:
            parts.append(f"Shots: {team.shot_count}, On Target: {team.shots_on_target}, Goals: {team.goals}")
        
        # Territory
        if team.avg_position_x is not None:
            parts.append(f"Avg Position: {team.avg_position_x:.1f}, Final Third: {team.final_third_entries}")
        
        # Spatial attack
        if team.left_flank_attacks_pct is not None:
            parts.append(f"Attack Distribution: L{team.left_flank_attacks_pct:.0%} C{team.center_attacks_pct:.0%} R{team.right_flank_attacks_pct:.0%}")
        
        # Defense
        if team.high_press_actions is not None:
            parts.append(f"High Press: {team.high_press_actions}, Low Block: {team.low_block_actions}")
        
        # Passing patterns
        if team.pass_width_spread is not None:
            parts.append(f"Pass Width: {team.pass_width_spread:.1f}, Backward Passes: {team.back_passes_pct:.0%}")
        
        parts.append("")
    
    parts.append(f"## Question\n{question}\n")
    parts.append("Provide tactical analysis with evidence from metrics.")
    
    return "\n".join(parts)
