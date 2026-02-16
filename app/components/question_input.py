"""Question input component for asking natural language questions about matches."""
from typing import Optional

import streamlit as st

from config import get_config

# Get example questions from config
_config = get_config()
EXAMPLE_QUESTIONS = _config.example_questions


def render_question_input() -> Optional[str]:
    """Render question input UI and return the submitted question.
    
    Returns:
        Question text if submitted, None otherwise
    """
    st.header("💬 Ask a Question")
    
    # Show example questions in an expander
    with st.expander("💡 Example Questions", expanded=False):
        st.markdown("Try questions like:")
        for question in EXAMPLE_QUESTIONS:
            if st.button(question, key=f"example_{hash(question)}", use_container_width=True):
                st.session_state.current_question = question
                st.rerun()
    
    # Question input
    question = st.text_area(
        label="Your question:",
        value=st.session_state.get("current_question", ""),
        placeholder="e.g., Why did Arsenal lose control after halftime?",
        height=100,
        help="Ask about team-level performance, tactics, or match dynamics.",
    )
    
    # Submit button
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        submit_button = st.button(
            "Get Explanation",
            type="primary",
            disabled=not question.strip(),
            use_container_width=True,
        )
    
    # Update session state
    st.session_state.current_question = question
    
    # Return question if submitted
    if submit_button and question.strip():
        return question.strip()
    
    return None


def render_question_input_simple() -> str:
    """Simplified question input without examples section.
    
    Returns:
        Current question text (may be empty)
    """
    question = st.text_input(
        "Ask a question:",
        value=st.session_state.get("current_question", ""),
        placeholder="Why did the team struggle to create chances?",
    )
    
    st.session_state.current_question = question
    return question
