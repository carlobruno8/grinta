"""Orchestration pipeline for StatsBomb data ingestion."""
import logging
from pathlib import Path
from typing import Optional

from ingestion.config import IngestionConfig
from ingestion.loaders import load_competitions, load_events, load_matches
from ingestion.normalizers import normalize_events
from ingestion.storage import (
    load_events as load_events_from_cache,
    save_competitions,
    save_events,
    save_events_df,
    save_matches,
)

logger = logging.getLogger(__name__)


class PipelineResult:
    """Result object from pipeline execution."""

    def __init__(self):
        self.success = True
        self.errors = []
        self.saved_raw_paths = []
        self.saved_processed_paths = []
        self.processed_match_ids = []

    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.success = False


def run_pipeline(config: Optional[IngestionConfig] = None, use_cache: bool = False) -> PipelineResult:
    """Run the full ingestion pipeline for a competition and season.

    Steps:
    1. Load competitions (optional, for reference)
    2. Load matches for competition + season
    3. Save raw matches
    4. For each match (or filtered list):
       a. Load events
       b. Save raw events
       c. Normalize events
       d. Save processed events

    Args:
        config: IngestionConfig instance. If None, loads from environment.
        use_cache: If True, skip API calls and use existing raw files from disk.
                  Only normalization and processed save will run.

    Returns:
        PipelineResult with success status, errors, and saved file paths
    """
    if config is None:
        from ingestion.config import get_ingestion_config

        config = get_ingestion_config()

    result = PipelineResult()

    try:
        # Step 1: Load competitions (optional, for reference)
        if not use_cache:
            try:
                competitions = load_competitions()
                save_competitions(competitions, config.raw_dir)
                logger.info("Loaded and saved competitions")
            except Exception as e:
                logger.warning(f"Failed to load competitions: {e}")
                # Non-fatal, continue

        # Step 2: Load matches
        if use_cache:
            try:
                matches = load_matches(config.competition_id, config.season_id, config.raw_dir)
                logger.info(f"Loaded matches from cache for competition {config.competition_id}, season {config.season_id}")
            except FileNotFoundError:
                result.add_error(f"Matches file not found in cache for competition {config.competition_id}, season {config.season_id}")
                return result
        else:
            try:
                matches = load_matches(config.competition_id, config.season_id)
                save_path = save_matches(matches, config.competition_id, config.season_id, config.raw_dir)
                result.saved_raw_paths.append(save_path)
                logger.info(f"Loaded and saved matches for competition {config.competition_id}, season {config.season_id}")
            except Exception as e:
                result.add_error(f"Failed to load matches: {e}")
                return result

        # Step 3: Extract match IDs
        if isinstance(matches, dict):
            # If dict keyed by match_id
            match_ids = list(matches.keys())
            # Convert string keys to int if needed
            match_ids = [int(mid) if isinstance(mid, str) else mid for mid in match_ids]
        elif isinstance(matches, list):
            # If list of match dicts, extract match_id from each
            match_ids = []
            for match in matches:
                if isinstance(match, dict):
                    match_id = match.get("match_id") or match.get("id")
                    if match_id:
                        match_ids.append(int(match_id))
        else:
            result.add_error(f"Unexpected matches format: {type(matches)}")
            return result

        # Filter to requested match_ids if specified
        if config.match_ids:
            match_ids = [mid for mid in match_ids if mid in config.match_ids]
            if not match_ids:
                result.add_error(f"None of the requested match IDs {config.match_ids} found in matches")
                return result

        logger.info(f"Processing {len(match_ids)} matches")

        # Step 4: Process each match
        for match_id in match_ids:
            try:
                match_result = run_match_events_pipeline(
                    match_id=match_id,
                    config=config,
                    use_cache=use_cache,
                )
                if match_result.success:
                    result.saved_raw_paths.extend(match_result.saved_raw_paths)
                    result.saved_processed_paths.extend(match_result.saved_processed_paths)
                    result.processed_match_ids.append(match_id)
                else:
                    result.errors.extend(match_result.errors)
                    logger.warning(f"Failed to process match {match_id}: {match_result.errors}")
            except Exception as e:
                error_msg = f"Error processing match {match_id}: {e}"
                result.add_error(error_msg)
                logger.error(error_msg, exc_info=True)

        if result.success:
            logger.info(f"Pipeline completed successfully. Processed {len(result.processed_match_ids)} matches.")
        else:
            logger.warning(f"Pipeline completed with errors. Processed {len(result.processed_match_ids)} matches.")

    except Exception as e:
        result.add_error(f"Pipeline failed: {e}")
        logger.error("Pipeline failed", exc_info=True)

    return result


def run_match_events_pipeline(
    match_id: int,
    config: Optional[IngestionConfig] = None,
    use_cache: bool = False,
) -> PipelineResult:
    """Run ingestion pipeline for a single match.

    Steps:
    1. Load events for the match
    2. Save raw events
    3. Normalize events
    4. Save processed events

    Args:
        match_id: Match ID to process
        config: IngestionConfig instance. If None, loads from environment.
        use_cache: If True, skip API call and use existing raw file from disk.

    Returns:
        PipelineResult with success status, errors, and saved file paths
    """
    if config is None:
        from ingestion.config import get_ingestion_config

        config = get_ingestion_config()

    result = PipelineResult()

    try:
        # Step 1: Load events
        if use_cache:
            try:
                events = load_events_from_cache(match_id, config.raw_dir)
                logger.info(f"Loaded events from cache for match {match_id}")
            except FileNotFoundError:
                result.add_error(f"Events file not found in cache for match {match_id}")
                return result
        else:
            try:
                events = load_events(match_id)
                save_path = save_events(events, match_id, config.raw_dir)
                result.saved_raw_paths.append(save_path)
                logger.info(f"Loaded and saved events for match {match_id}")
            except Exception as e:
                result.add_error(f"Failed to load events for match {match_id}: {e}")
                return result

        # Step 2: Normalize events
        try:
            df = normalize_events(events, match_id=match_id)
            logger.info(f"Normalized {len(df)} events for match {match_id}")
        except Exception as e:
            result.add_error(f"Failed to normalize events for match {match_id}: {e}")
            return result

        # Step 3: Save processed events
        try:
            save_path = save_events_df(df, match_id, config.processed_dir, config.processed_format)
            result.saved_processed_paths.append(save_path)
            logger.info(f"Saved processed events for match {match_id} to {save_path}")
        except Exception as e:
            result.add_error(f"Failed to save processed events for match {match_id}: {e}")
            return result

    except Exception as e:
        result.add_error(f"Match pipeline failed for match {match_id}: {e}")
        logger.error(f"Match pipeline failed for match {match_id}", exc_info=True)

    return result
