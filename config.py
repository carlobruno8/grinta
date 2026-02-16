"""Unified configuration for Grinta.

All configuration in one place - paths, ingestion settings, LLM settings, and UI settings.
Load from environment variables with sensible defaults.
"""
import os
import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


@dataclass
class GrintaConfig:
    """Unified configuration for all Grinta modules.
    
    Attributes:
        # Data paths
        raw_dir: Directory for storing raw JSON files from StatsBomb
        processed_dir: Directory for storing processed DataFrames
        processed_format: Output format for processed data ("csv" | "parquet")
        
        # Ingestion settings
        competition_id: StatsBomb competition ID (required for ingestion)
        season_id: StatsBomb season ID (required for ingestion)
        match_ids: Optional list of specific match IDs to ingest
        
        # LLM / Reasoning settings
        api_key: Google AI API key for Gemini
        model: Gemini model name (e.g., "gemini-1.5-flash", "gemini-1.5-pro")
        temperature: Temperature for generation (0.0 = deterministic, 2.0 = creative)
        max_tokens: Maximum tokens in LLM response
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts for failed LLM requests
        
        # UI settings
        colors: Color palette for Streamlit UI
        example_questions: Example questions to show users
        default_match_id: Default match ID for testing
        page_config: Streamlit page configuration
    """
    
    # Data paths
    raw_dir: Path = Path("data/raw")
    processed_dir: Path = Path("data/processed")
    processed_format: str = "parquet"
    
    # Ingestion settings
    competition_id: Optional[int] = None
    season_id: Optional[int] = None
    match_ids: Optional[list[int]] = None
    
    # LLM / Reasoning settings
    api_key: Optional[str] = None
    model: str = "gemini-2.5-flash"
    temperature: float = 0.0
    max_tokens: int = 4000  # Increased to avoid truncation
    timeout: int = 60
    max_retries: int = 3
    
    # UI settings
    colors: dict = field(default_factory=lambda: {
        "primary": "#1f77b4",  # Blue
        "secondary": "#6c757d",  # Gray
        "accent": "#17a2b8",  # Teal
        "success": "#28a745",  # Green
        "warning": "#ffc107",  # Yellow
        "error": "#dc3545",  # Red
        "background": "#ffffff",
        "text": "#333333",
    })
    example_questions: list[str] = field(default_factory=lambda: [
        "Why did Liverpool concede in the last 10 minutes?",
        "Why did Arsenal lose control after halftime?",
        "Why did the team struggle to create chances?",
        "How did Manchester City dominate possession?",
        "What happened in the second half?",
    ])
    default_match_id: int = 22912
    page_config: dict = field(default_factory=lambda: {
        "page_title": "Grinta - Football Analytics",
        "page_icon": "⚽",
        "layout": "wide",
        "initial_sidebar_state": "auto",
    })
    
    def __post_init__(self):
        """Validate and normalize configuration."""
        # Convert string paths to Path objects
        if isinstance(self.raw_dir, str):
            self.raw_dir = Path(self.raw_dir)
        if isinstance(self.processed_dir, str):
            self.processed_dir = Path(self.processed_dir)
        
        # Ensure directories exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate processed format
        if self.processed_format not in ("csv", "parquet"):
            raise ValueError(
                f"processed_format must be 'csv' or 'parquet', got '{self.processed_format}'"
            )
        
        # Validate LLM settings (if API key is provided)
        if self.api_key:
            # Validate temperature
            if not 0.0 <= self.temperature <= 2.0:
                raise ValueError(
                    f"Temperature must be between 0.0 and 2.0, got {self.temperature}"
                )
            
            # Warn about unknown models
            valid_models = [
                "gemini-1.5-flash", "gemini-1.5-pro",
                "gemini-1.0-pro", "gemini-pro"
            ]
            if self.model not in valid_models:
                warnings.warn(
                    f"Model '{self.model}' is not in the known list. Proceeding anyway."
                )
    
    @classmethod
    def from_env(cls) -> "GrintaConfig":
        """Load configuration from environment variables.
        
        Environment variables:
            # Data paths
            GRINTA_RAW_DIR: Raw data directory (default: "data/raw")
            GRINTA_PROCESSED_DIR: Processed data directory (default: "data/processed")
            GRINTA_PROCESSED_FORMAT: Output format (default: "parquet")
            
            # Ingestion
            GRINTA_COMPETITION_ID: Competition ID (optional)
            GRINTA_SEASON_ID: Season ID (optional)
            GRINTA_MATCH_ID: Comma-separated match IDs (optional, e.g., "123,456,789")
            
            # LLM / Reasoning
            GOOGLE_API_KEY: Google AI API key (required for reasoning)
            GRINTA_LLM_MODEL: Model to use (default: "gemini-1.5-flash")
            GRINTA_LLM_TEMPERATURE: Temperature (default: 0.0)
            GRINTA_LLM_MAX_TOKENS: Max tokens (default: 2000)
            GRINTA_LLM_TIMEOUT: Timeout in seconds (default: 60)
            GRINTA_LLM_MAX_RETRIES: Max retries (default: 3)
        
        Returns:
            GrintaConfig instance with values loaded from environment
        """
        # Parse match IDs
        match_ids_str = os.getenv("GRINTA_MATCH_ID")
        match_ids = None
        if match_ids_str:
            match_ids = [int(mid.strip()) for mid in match_ids_str.split(",")]
        
        # Parse competition and season IDs (optional)
        competition_id = os.getenv("GRINTA_COMPETITION_ID")
        season_id = os.getenv("GRINTA_SEASON_ID")
        
        return cls(
            # Data paths
            raw_dir=Path(os.getenv("GRINTA_RAW_DIR", "data/raw")),
            processed_dir=Path(os.getenv("GRINTA_PROCESSED_DIR", "data/processed")),
            processed_format=os.getenv("GRINTA_PROCESSED_FORMAT", "parquet"),
            
            # Ingestion
            competition_id=int(competition_id) if competition_id else None,
            season_id=int(season_id) if season_id else None,
            match_ids=match_ids,
            
            # LLM / Reasoning
            api_key=os.getenv("GOOGLE_API_KEY"),
            model=os.getenv("GRINTA_LLM_MODEL", "gemini-2.5-flash"),
            temperature=float(os.getenv("GRINTA_LLM_TEMPERATURE", "0.0")),
            max_tokens=int(os.getenv("GRINTA_LLM_MAX_TOKENS", "4000")),
            timeout=int(os.getenv("GRINTA_LLM_TIMEOUT", "60")),
            max_retries=int(os.getenv("GRINTA_LLM_MAX_RETRIES", "3")),
        )
    
    def require_ingestion(self) -> None:
        """Validate that ingestion settings are configured.
        
        Raises:
            ValueError: If competition_id or season_id are not set
        """
        if self.competition_id is None:
            raise ValueError(
                "GRINTA_COMPETITION_ID environment variable is required for ingestion"
            )
        if self.season_id is None:
            raise ValueError(
                "GRINTA_SEASON_ID environment variable is required for ingestion"
            )
    
    def require_reasoning(self) -> None:
        """Validate that reasoning/LLM settings are configured.
        
        Raises:
            ValueError: If API key is not set
        """
        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable is required for reasoning. "
                "Get your key at https://makersuite.google.com/app/apikey"
            )


# Global config instance (lazy loaded)
_config: Optional[GrintaConfig] = None


def get_config() -> GrintaConfig:
    """Get the global config instance (loads from environment on first call).
    
    Returns:
        GrintaConfig instance
    """
    global _config
    if _config is None:
        _config = GrintaConfig.from_env()
    return _config


def reset_config() -> None:
    """Reset the global config instance (useful for testing)."""
    global _config
    _config = None
