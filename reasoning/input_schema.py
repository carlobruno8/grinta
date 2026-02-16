"""Input schema for LLM reasoning.

Defines the bounded reasoning input object that packages all team-level metrics
for structured, evidence-based explanations.
"""
from typing import Optional
from pydantic import BaseModel, Field


class TeamMetrics(BaseModel):
    """Team-level metrics for a specific time window.
    
    All metrics are computed from event data and represent observable facts.
    """
    team_id: int
    team_name: str
    
    # Possession metrics
    possession_share: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0,
        description="Possession share as fraction (0-1) based on pass counts"
    )
    pass_count: Optional[int] = Field(None, ge=0, description="Total pass attempts")
    successful_passes: Optional[int] = Field(None, ge=0, description="Successful passes")
    pass_completion_rate: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0, 
        description="Successful passes / total passes"
    )
    
    # Shot metrics
    shot_count: Optional[int] = Field(None, ge=0, description="Total shot attempts")
    shots_on_target: Optional[int] = Field(None, ge=0, description="Shots on target")
    goals: Optional[int] = Field(None, ge=0, description="Goals scored")
    
    # Territorial metrics
    avg_position_x: Optional[float] = Field(
        None,
        description="Average x-coordinate of team events (0-120 scale)"
    )
    avg_position_y: Optional[float] = Field(
        None,
        description="Average y-coordinate of team events (0-80 scale)"
    )
    final_third_entries: Optional[int] = Field(
        None,
        ge=0,
        description="Number of events in opponent's final third (x >= 80)"
    )
    
    # Spatial distribution metrics (tactical insights)
    left_flank_attacks_pct: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Percentage of attacks down left flank (0-1)"
    )
    center_attacks_pct: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Percentage of attacks through center (0-1)"
    )
    right_flank_attacks_pct: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Percentage of attacks down right flank (0-1)"
    )
    attacking_half_actions: Optional[int] = Field(
        None,
        ge=0,
        description="Number of attacking actions in opponent's half"
    )
    
    # Defensive positioning
    high_press_actions: Optional[int] = Field(
        None,
        ge=0,
        description="Defensive actions in opponent's half (indicates pressing intensity)"
    )
    low_block_actions: Optional[int] = Field(
        None,
        ge=0,
        description="Defensive actions in own third (indicates deep defending)"
    )
    
    # Passing patterns
    pass_width_spread: Optional[float] = Field(
        None,
        description="Standard deviation of pass y-coordinates (higher = wider play)"
    )
    back_passes_pct: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Percentage of backward passes (0-1, higher = more cautious)"
    )
    
    def model_post_init(self, __context):
        """Calculate derived metrics after initialization."""
        # Calculate pass completion rate if we have the data
        if self.pass_count is not None and self.successful_passes is not None:
            if self.pass_count > 0:
                self.pass_completion_rate = self.successful_passes / self.pass_count
            else:
                self.pass_completion_rate = 0.0


class TimeWindowContext(BaseModel):
    """Context about the time window being analyzed."""
    description: str = Field(description="Human-readable description (e.g., 'Full Match', 'Last 10 minutes')")
    period: Optional[int] = Field(None, description="Period number if filtered (1, 2, etc.)")
    time_filter: Optional[str] = Field(None, description="Filter type applied (e.g., 'last_10_min', 'period_2')")


class MatchContext(BaseModel):
    """Context about the match being analyzed."""
    match_id: int
    home_team: str
    away_team: str
    competition: Optional[str] = Field(None, description="Competition name")
    season: Optional[str] = Field(None, description="Season identifier")
    match_date: Optional[str] = Field(None, description="Match date (ISO format)")


class ReasoningInput(BaseModel):
    """Complete input package for LLM reasoning.
    
    This is the bounded input object that contains all metrics the LLM is allowed to reason over.
    The LLM must not use any external knowledge or compute any metrics.
    """
    match_context: MatchContext
    time_window: TimeWindowContext
    team_metrics: list[TeamMetrics] = Field(
        description="Metrics for all teams in the match (typically 2)"
    )
    question: str = Field(description="The user's question to be answered")
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return self.model_dump()
    
    def to_json(self, **kwargs) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(**kwargs)
    
    def get_team_by_name(self, team_name: str) -> Optional[TeamMetrics]:
        """Get metrics for a specific team by name."""
        for team in self.team_metrics:
            if team.team_name.lower() == team_name.lower():
                return team
        return None
    
    def get_team_by_id(self, team_id: int) -> Optional[TeamMetrics]:
        """Get metrics for a specific team by ID."""
        for team in self.team_metrics:
            if team.team_id == team_id:
                return team
        return None
