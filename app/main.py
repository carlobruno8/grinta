"""
Grinta - Evidence-Based Football Analytics

A Streamlit app for generating grounded, auditable explanations of match outcomes.
Just ask a question in natural language - Grinta will figure out the rest.
"""
import sys
from pathlib import Path

import streamlit as st

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import GrintaConfig
from app.question_parser import parse_question
from app.components.metrics_display import render_metrics_display
from app.components.explanation import (
    render_explanation_from_response,
    render_explanation_placeholder,
    render_explanation_loading,
    render_explanation_error,
)

# Get config instance
config = GrintaConfig()
PAGE_CONFIG = config.page_config
EXAMPLE_QUESTIONS = config.example_questions


def init_session_state():
    """Initialize session state variables."""
    if "current_question" not in st.session_state:
        st.session_state.current_question = ""
    if "parsed_query" not in st.session_state:
        st.session_state.parsed_query = None
    if "metrics_data" not in st.session_state:
        st.session_state.metrics_data = None
    if "explanation_response" not in st.session_state:
        st.session_state.explanation_response = None
    if "show_results" not in st.session_state:
        st.session_state.show_results = False


def load_match_metrics(match_id: int, period: int = None, last_n_minutes: float = None):
    """Load metrics for the specified match and time window.
    
    Args:
        match_id: StatsBomb match ID
        period: Optional period filter
        last_n_minutes: Optional time window
    """
    try:
        from features import get_match_metrics_multi_segment
        
        with st.spinner(f"Loading match data..."):
            # Build segments list
            segments = []
            if period:
                segments.append({"period": period})
            if last_n_minutes:
                seg = {"last_n_minutes": last_n_minutes}
                if period:
                    seg["period"] = period
                segments.append(seg)
            
            # Always include full match for context
            if not segments:
                segments.append({"period": 2})
                segments.append({"period": 2, "last_n_minutes": 10})
            
            metrics = get_match_metrics_multi_segment(match_id, segments=segments)
            st.session_state.metrics_data = metrics
            return True
    except FileNotFoundError:
        st.error(f"❌ No data found for match {match_id}")
        return False
    except Exception as e:
        st.error(f"❌ Error loading metrics: {str(e)}")
        return False


def process_question(question: str):
    """Process the question and load relevant data.
    
    Args:
        question: User's natural language question
    """
    # Parse the question
    with st.spinner("Understanding your question..."):
        parsed = parse_question(question)
        st.session_state.parsed_query = parsed
    
    # Check if we found a match
    if parsed["match_id"] is None:
        if len(parsed["available_matches"]) == 0:
            st.error("❌ No match data available. Run the ingestion pipeline first:")
            st.code("python3 -m ingestion", language="bash")
            return False
        else:
            st.error("❌ Could not identify which match you're asking about.")
            st.info("💡 Try including team names like: 'Why did Liverpool concede late?'")
            return False
    
    # Load the match data
    if not load_match_metrics(
        parsed["match_id"],
        period=parsed["period"],
        last_n_minutes=parsed["last_n_minutes"],
    ):
        return False
    
    # Generate explanation using reasoning module
    try:
        from reasoning import generate_explanation
        
        # Build time filter from parsed query
        time_filter = None
        if parsed["last_n_minutes"]:
            time_filter = f"last_{int(parsed['last_n_minutes'])}_min"
        elif parsed["period"]:
            time_filter = f"period_{parsed['period']}"
        
        with st.spinner("Generating AI explanation..."):
            response = generate_explanation(
                match_id=parsed["match_id"],
                question=question,
                time_filter=time_filter
            )
            
            # Convert response to dict format expected by UI
            st.session_state.explanation_response = {
                "explanation": {
                    "summary": response.explanation.summary,
                    "claims": [
                        {
                            "statement": claim.statement,
                            "confidence": claim.confidence,
                            "supporting_evidence": [
                                {
                                    "metric_name": ev.metric_name,
                                    "value": ev.value,
                                    "interpretation": ev.interpretation
                                }
                                for ev in claim.supporting_evidence
                            ]
                        }
                        for claim in response.explanation.claims
                    ],
                    "caveats": response.explanation.caveats,
                    "overall_confidence": response.explanation.overall_confidence
                }
            }
    except Exception as e:
        st.error(f"❌ Failed to generate explanation: {str(e)}")
        st.info("💡 Make sure GOOGLE_API_KEY is set in your .env file")
        st.session_state.explanation_response = None
        return False
    
    st.session_state.show_results = True
    return True


def main():
    """Main application entry point."""
    # Set page configuration
    st.set_page_config(**PAGE_CONFIG)
    
    # Initialize session state
    init_session_state()
    
    # Header
    st.title("⚽ Grinta")
    st.markdown("**Evidence-based football analytics through natural language**")
    st.markdown("Just ask a question about a match - Grinta will figure out the rest.")
    
    st.divider()
    
    # Sidebar with information
    with st.sidebar:
        st.header("How to Use")
        st.markdown("""
        1. **Ask a question** in natural language
        2. Grinta identifies the match and context
        3. See the answer with supporting evidence
        """)
        
        st.divider()
        
        st.subheader("Example Questions")
        for question in EXAMPLE_QUESTIONS:
            st.caption(f"• {question}")
        
        st.divider()
        
        st.caption("**Phase 1**: Team-level analysis only")
        st.caption("**Note**: Mock explanations (LLM integration coming)")
    
    # Main question input - HERO SECTION
    st.markdown("### Ask Grinta")
    
    # Show clickable examples above the input
    with st.expander("💡 See example questions", expanded=False):
        col1, col2 = st.columns(2)
        for idx, question in enumerate(EXAMPLE_QUESTIONS):
            col = col1 if idx % 2 == 0 else col2
            with col:
                if st.button(question, key=f"ex_{idx}", use_container_width=True):
                    st.session_state.current_question = question
                    st.rerun()
    
    # Large text input
    question = st.text_area(
        label="Your question:",
        value=st.session_state.current_question,
        placeholder="e.g., Why did Liverpool concede in the last 10 minutes against Tottenham?",
        height=120,
        label_visibility="collapsed",
    )
    
    # Centered submit button
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        submit = st.button("Get Answer", type="primary", use_container_width=True)
    
    st.session_state.current_question = question
    
    # Process question if submitted
    if submit and question.strip():
        # Reset previous results
        st.session_state.show_results = False
        st.session_state.metrics_data = None
        st.session_state.explanation_response = None
        
        process_question(question.strip())
    
    # Show results if available
    if st.session_state.show_results:
        st.divider()
        
        # Show what Grinta understood
        if st.session_state.parsed_query:
            parsed = st.session_state.parsed_query
            
            with st.expander("🔍 What Grinta understood", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if parsed["teams"]:
                        st.metric("Teams identified", ", ".join(parsed["teams"]))
                    else:
                        st.caption("No specific teams mentioned")
                
                with col2:
                    if parsed["period"]:
                        st.metric("Period", f"Half {parsed['period']}")
                    elif parsed["last_n_minutes"]:
                        st.metric("Time window", f"Last {int(parsed['last_n_minutes'])} min")
                    else:
                        st.caption("Full match")
                
                with col3:
                    st.metric("Match ID", parsed["match_id"])
        
        st.divider()
        
        # Explanation first (what user cares about)
        if st.session_state.explanation_response:
            from app.components.explanation import render_explanation_from_response
            render_explanation_from_response(st.session_state.explanation_response)
        
        st.divider()
        
        # Metrics as supporting evidence
        if st.session_state.metrics_data:
            st.markdown("### 📊 Supporting Evidence")
            st.caption("These are the metrics used to generate the explanation above")
            render_metrics_display(st.session_state.metrics_data)
    
    # Footer
    st.divider()
    st.caption("Powered by StatsBomb Open Data • Phase 1: Team-level explanations only")


if __name__ == "__main__":
    main()
