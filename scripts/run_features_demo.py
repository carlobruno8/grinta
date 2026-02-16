#!/usr/bin/env python3
"""Demo: load processed events for a match and print team-level metrics."""
import json
import os
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from features import get_match_metrics, get_match_metrics_multi_segment

# Use match we ingested earlier
MATCH_ID = 22912


def main():
    print("Loading processed data and computing metrics for match", MATCH_ID)
    print("(Processed file must exist: data/processed/events_22912.parquet)\n")
    try:
        metrics = get_match_metrics(MATCH_ID)
    except FileNotFoundError as e:
        print("Error:", e)
        print("Run the ingestion pipeline first for this match (e.g. test_manual.py).")
        return 1
    print("Full match metrics:")
    print(json.dumps(metrics, indent=2))
    print("\n--- Last 10 minutes ---")
    last10 = get_match_metrics(MATCH_ID, last_n_minutes=10)
    print(json.dumps(last10, indent=2))
    print("\n--- Multi-segment (full + period 2 + last 10 min of P2) ---")
    multi = get_match_metrics_multi_segment(
        MATCH_ID,
        segments=[{"period": 2}, {"period": 2, "last_n_minutes": 10}],
    )
    print(json.dumps(multi, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
