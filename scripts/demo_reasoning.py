#!/usr/bin/env python3
"""Example demonstration of the reasoning module.

This script shows how to:
1. Load match events
2. Generate explanations with different time filters
3. Access structured output

Requirements:
- Processed match events must exist (run ingestion first)
- GOOGLE_API_KEY environment variable must be set
"""
import os
import sys

from reasoning import generate_explanation


def demo_full_match_explanation(match_id: int):
    """Generate explanation for full match."""
    print("\n" + "=" * 80)
    print("DEMO 1: Full Match Explanation")
    print("=" * 80)
    
    response = generate_explanation(
        match_id=match_id,
        question="What were the key differences between the two teams?"
    )
    
    print(f"\n📊 Summary:")
    print(f"  {response.explanation.summary}")
    
    print(f"\n🔍 Claims ({len(response.explanation.claims)} total):")
    for i, claim in enumerate(response.explanation.claims, 1):
        print(f"\n  {i}. {claim.statement}")
        print(f"     Confidence: {claim.confidence}")
        print(f"     Evidence:")
        for evidence in claim.supporting_evidence:
            print(f"       - {evidence.metric_name}: {evidence.value}")
            print(f"         → {evidence.interpretation}")
    
    if response.explanation.caveats:
        print(f"\n⚠️  Caveats:")
        for caveat in response.explanation.caveats:
            print(f"  - {caveat}")
    
    print(f"\n✅ Overall Confidence: {response.explanation.overall_confidence}")


def demo_time_filtered_explanation(match_id: int):
    """Generate explanation for last 10 minutes."""
    print("\n" + "=" * 80)
    print("DEMO 2: Last 10 Minutes Analysis")
    print("=" * 80)
    
    response = generate_explanation(
        match_id=match_id,
        question="What changed in the final 10 minutes of the match?",
        time_filter="last_10_min"
    )
    
    print(f"\n📊 Summary:")
    print(f"  {response.explanation.summary}")
    
    print(f"\n🔍 Key Claims:")
    for claim in response.explanation.claims[:2]:  # Show first 2 claims
        print(f"  - {claim.statement} (confidence: {claim.confidence})")


def demo_period_analysis(match_id: int):
    """Generate explanation for second half."""
    print("\n" + "=" * 80)
    print("DEMO 3: Second Half Analysis")
    print("=" * 80)
    
    response = generate_explanation(
        match_id=match_id,
        question="How did the teams perform in the second half?",
        time_filter="period_2"
    )
    
    print(f"\n📊 Summary:")
    print(f"  {response.explanation.summary}")
    
    print(f"\n🎯 Overall Assessment: {response.explanation.overall_confidence} confidence")


def main():
    """Run all demos."""
    # Check for API key
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        print("\nSet your API key:")
        print('  export GOOGLE_API_KEY="your-google-api-key"')
        sys.exit(1)
    
    # Default to a well-known match (Champions League 2018/2019)
    # This is Barcelona vs Liverpool - a famous comeback match
    match_id = int(os.getenv("GRINTA_DEMO_MATCH_ID", "22912"))
    
    print("\n" + "=" * 80)
    print("GRINTA REASONING MODULE DEMO")
    print("=" * 80)
    print(f"\nMatch ID: {match_id}")
    print("\nNote: This demo requires processed match events.")
    print("Run ingestion first if the match data doesn't exist:")
    print(f"  python3 -m ingestion")
    
    try:
        # Demo 1: Full match explanation
        demo_full_match_explanation(match_id)
        
        # Demo 2: Time-filtered explanation
        demo_time_filtered_explanation(match_id)
        
        # Demo 3: Period-specific analysis
        demo_period_analysis(match_id)
        
        print("\n" + "=" * 80)
        print("✅ Demo completed successfully!")
        print("=" * 80)
        print("\nFor more examples, see: reasoning/contract.md")
        
    except FileNotFoundError:
        print(f"\n❌ Error: Match {match_id} events not found")
        print("\nRun ingestion first:")
        print("  export GRINTA_COMPETITION_ID=16")
        print("  export GRINTA_SEASON_ID=4")
        print("  python3 -m ingestion")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Error: {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
