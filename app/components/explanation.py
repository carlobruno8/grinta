"""Explanation display component for showing AI-generated match explanations."""
from typing import Any, Dict, List, Optional

import streamlit as st


def render_explanation_mock(question: str) -> None:
    """Render a mock explanation (placeholder for LLM integration).
    
    Args:
        question: The question that was asked
    """
    st.header("💭 AI-Generated Explanation")
    
    # Disclaimer
    st.info(
        "ℹ️ This explanation is generated based only on the metrics shown above. "
        "No external knowledge is used."
    )
    
    # Mock explanation
    with st.container():
        st.subheader("Summary")
        st.markdown(
            "Based on the match metrics, Team A maintained higher possession (62%) "
            "and completed more passes (487 vs 312), indicating territorial control. "
            "However, Team B was more efficient in attack with 8 shots compared to Team A's 6."
        )
        
        st.subheader("Key Claims")
        
        # Claim 1
        with st.expander("🔹 Team A controlled possession and territory", expanded=True):
            st.markdown("**Evidence:**")
            st.markdown("- Possession: 62% vs 38%")
            st.markdown("- Successful passes: 487 vs 312")
            st.markdown("- Average position: (58.2, 40.1) vs (45.8, 39.2)")
            st.markdown("**Confidence:** High")
        
        # Claim 2
        with st.expander("🔹 Team B created more attacking opportunities", expanded=True):
            st.markdown("**Evidence:**")
            st.markdown("- Shots: 8 vs 6")
            st.markdown("- Shots on target: 4 vs 3")
            st.markdown("- Final third entries: 28 vs 24")
            st.markdown("**Confidence:** High")
        
        st.subheader("Caveats")
        st.markdown("- ⚠️ Possession alone doesn't determine match outcome")
        st.markdown("- ⚠️ No data on defensive actions (tackles, blocks)")
        st.markdown("- ⚠️ Shot quality metrics not available")
        
        # Overall confidence
        st.metric(
            label="Overall Confidence",
            value="Medium-High",
            help="Based on availability and quality of supporting metrics",
        )


def render_explanation_from_response(response: Dict[str, Any]) -> None:
    """Render explanation from actual LLM response.
    
    Args:
        response: Structured response from reasoning module
    """
    st.header("💭 AI-Generated Explanation")
    
    # Disclaimer
    st.info(
        "ℹ️ This explanation is generated based only on the metrics shown above. "
        "No external knowledge is used."
    )
    
    explanation = response.get("explanation", {})
    
    # Summary
    with st.container():
        st.subheader("Summary")
        summary = explanation.get("summary", "No summary available.")
        st.markdown(summary)
        
        # Claims
        claims = explanation.get("claims", [])
        if claims:
            st.subheader("Key Claims")
            
            for idx, claim in enumerate(claims, 1):
                statement = claim.get("statement", "")
                confidence = claim.get("confidence", "unknown")
                evidence = claim.get("supporting_evidence", [])
                
                with st.expander(f"🔹 {statement}", expanded=(idx == 1)):
                    if evidence:
                        st.markdown("**Evidence:**")
                        for ev in evidence:
                            metric_name = ev.get("metric_name", "")
                            value = ev.get("value", "")
                            st.markdown(f"- {metric_name}: {value}")
                    
                    st.markdown(f"**Confidence:** {confidence.title()}")
        
        # Caveats
        caveats = explanation.get("caveats", [])
        if caveats:
            st.subheader("Caveats")
            for caveat in caveats:
                st.markdown(f"- ⚠️ {caveat}")
        
        # Overall confidence
        overall_confidence = explanation.get("overall_confidence", "unknown")
        st.metric(
            label="Overall Confidence",
            value=overall_confidence.title() if isinstance(overall_confidence, str) else overall_confidence,
            help="Based on availability and quality of supporting metrics",
        )


def render_explanation_loading() -> None:
    """Show loading state while generating explanation."""
    st.header("💭 AI-Generated Explanation")
    with st.spinner("Generating explanation..."):
        st.info("Analyzing match metrics and building explanation...")


def render_explanation_error(error_message: str) -> None:
    """Show error state if explanation generation fails.
    
    Args:
        error_message: Description of the error
    """
    st.header("💭 AI-Generated Explanation")
    st.error(f"❌ Failed to generate explanation: {error_message}")
    st.markdown("**Troubleshooting:**")
    st.markdown("- Check that GOOGLE_API_KEY is set in environment")
    st.markdown("- Verify the match has valid metrics data")
    st.markdown("- Try rephrasing your question")


def render_explanation_placeholder() -> None:
    """Show placeholder when no explanation has been requested yet."""
    st.header("💭 AI-Generated Explanation")
    st.info("👆 Ask a question above to get an AI-generated explanation")
