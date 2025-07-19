"""
MathGraph Streamlit Web Interface

A user-friendly web interface for the hybrid mathematical reasoning system.
"""
import streamlit as st
import time

# Import the MathGraph system
from src.mathgraph import MathReasoningSystem, MathGraphAPI
import re


def display_mathematical_explanation_properly(explanation: str):
    """
    Display mathematical explanations with proper inline LaTeX rendering.
    
    Uses the approach: st.write(f"Text with ${math}$ more text") 
    to maintain natural text flow while rendering math correctly.
    """
    if not explanation:
        return
    
    # Split explanation into paragraphs for better formatting
    paragraphs = explanation.split('\n\n')
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # Check if this is a display math block (starts and ends with $$)
        if paragraph.startswith('$$') and paragraph.endswith('$$'):
            # Display math - use st.latex
            math_content = paragraph[2:-2].strip()
            st.latex(math_content)
        else:
            # Regular paragraph with potential inline math
            # Use st.write with the inline LaTeX approach
            st.write(paragraph)


def initialize_session_state():
    """Initialize session state variables."""
    if "system" not in st.session_state:
        st.session_state.system = MathReasoningSystem(enable_logging=False)
    
    if "api" not in st.session_state:
        st.session_state.api = MathGraphAPI()
    
    if "problem_history" not in st.session_state:
        st.session_state.problem_history = []
    
    if "current_response" not in st.session_state:
        st.session_state.current_response = None


def display_header():
    """Display the application header."""
    st.set_page_config(
        page_title="MathGraph - Hybrid Mathematical Reasoning",
        page_icon="🔬",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔬 MathGraph: Hybrid Mathematical Reasoning System")
    st.markdown("""
    **Combining Large Language Models with Formal Logic for Mathematical Problem Solving**
    
    This system demonstrates a novel hybrid approach: LLMs handle natural language understanding 
    while formal reasoning engines ensure mathematical rigor and correctness.
    """)


def display_sidebar():
    """Display the sidebar with examples and configuration."""
    with st.sidebar:
        st.header("📝 Example Problems")
        
        example_categories = {
            "Algebraic Equations": [
                "If x + 5 = 12, find x",
                "If 3y = 21, what is y?",
                "If 2z - 4 = 10, find z"
            ],
            "Algebraic Identities": [
                "(a^n + b^n)(a^n - b^n) = a^(2n) - b^(2n)",
                "(x + y)^2 = x^2 + 2xy + y^2",
                "(a + b)(a - b) = a^2 - b^2"
            ],
            "Polynomial Theory": [
                "If a polynomial f(x) is divided by x−a, the remainder is f(a)",
                "If p(x) = x^2 + 3x + 2 and x = -1, find p(-1)"
            ],
            "Number Theory": [
                "If n is even, prove that 2n is even",
                "If a is odd and b is odd, prove that a + b is even"
            ],
            "Inequalities": [
                "If a > b and b > c, prove a > c",
                "If x > 5 and 5 > 2, prove x > 2"
            ]
        }
        
        for category, examples in example_categories.items():
            st.subheader(f"**{category}**")
            for example in examples:
                if st.button(example, key=f"example_{example}", use_container_width=True):
                    st.session_state.selected_example = example
        
        st.divider()
        
        # System configuration
        st.header("⚙️ Configuration")
        
        max_steps = st.slider("Max Proof Steps", 5, 50, 20)
        show_analysis = st.checkbox("Show Problem Analysis", value=True)
        show_formal = st.checkbox("Show Formal Representation", value=True)
        show_steps = st.checkbox("Show Proof Steps", value=True)
        
        st.session_state.config = {
            "max_steps": max_steps,
            "show_analysis": show_analysis,
            "show_formal": show_formal,
            "show_steps": show_steps
        }
        
        st.divider()
        
        # System health check
        st.header("🏥 System Health")
        if st.button("Check System Health", use_container_width=True):
            with st.spinner("Checking system health..."):
                health = st.session_state.api.health_check()
                if health["healthy"]:
                    st.success("✅ System is healthy")
                else:
                    st.error("❌ System has issues")
                    for issue in health["issues"]:
                        st.error(f"• {issue}")


def display_main_interface():
    """Display the main problem-solving interface."""
    
    # Problem input
    st.header("🧮 Mathematical Problem Solver")
    
    # Use example if selected
    if hasattr(st.session_state, 'selected_example'):
        default_problem = st.session_state.selected_example
        del st.session_state.selected_example
    else:
        default_problem = ""
    
    problem_text = st.text_area(
        "Enter your mathematical problem in natural language:",
        value=default_problem,
        height=100,
        placeholder="Example: If x + 3 = 10, find x"
    )
    
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        solve_button = st.button("🔍 Solve Problem", type="primary", use_container_width=True)
    
    with col2:
        clear_button = st.button("🗑️ Clear", use_container_width=True)
    
    if clear_button:
        st.session_state.current_response = None
        st.rerun()
    
    # Process problem
    if solve_button and problem_text.strip():
        with st.spinner("🧠 Processing problem... This may take a few seconds."):
            try:
                # Configure system
                st.session_state.system.configure_system({
                    "max_iterations": st.session_state.config["max_steps"]
                })
                
                # Solve problem
                response = st.session_state.system.solve_problem(
                    problem_text,
                    {
                        "show_analysis": st.session_state.config["show_analysis"],
                        "max_steps": st.session_state.config["max_steps"]
                    }
                )
                
                # Store response and add to history
                st.session_state.current_response = response
                st.session_state.problem_history.append({
                    "problem": problem_text,
                    "response": response,
                    "timestamp": time.time()
                })
                
            except Exception as e:
                st.error(f"❌ Error processing problem: {str(e)}")
                st.error("Please check your Azure OpenAI configuration.")


def display_results():
    """Display the results of problem solving."""
    if st.session_state.current_response is None:
        return
    
    response = st.session_state.current_response
    
    st.divider()
    st.header("📊 Results")
    
    # Success/failure indicator
    if response.success:
        if response.proof_result and response.proof_result.goal_achieved:
            st.success("✅ **Problem Solved Successfully!**")
        else:
            st.warning("⚠️ **Problem Processed but Solution Incomplete**")
    else:
        st.error("❌ **Problem Solving Failed**")
        st.error(f"Error: {response.error_message}")
        return
    
    # Display metadata
    if response.metadata:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Problem Type", response.metadata.get("problem_type", "unknown").title())
        
        with col2:
            confidence = response.metadata.get("extraction_confidence", 0.0)
            st.metric("Extraction Confidence", f"{confidence:.1%}")
        
        with col3:
            processing_time = response.metadata.get("processing_time", 0.0)
            st.metric("Processing Time", f"{processing_time:.2f}s")
        
        with col4:
            if response.proof_result:
                st.metric("Proof Steps", len(response.proof_result.steps))
    
    # Problem Analysis
    if st.session_state.config["show_analysis"] and response.analysis:
        st.subheader("🔍 Problem Analysis")
        display_mathematical_explanation_properly(response.analysis)
    
    # Formal Representation
    if st.session_state.config["show_formal"] and response.formal_problem:
        st.subheader("🧮 Formal Representation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Initial Facts:**")
            for fact in response.formal_problem.facts:
                st.code(str(fact), language="text")
            
            st.markdown("**Goal:**")
            st.code(str(response.formal_problem.goal), language="text")
        
        with col2:
            st.markdown("**Available Rules:**")
            for rule in response.formal_problem.rules:
                st.code(f"{rule.name}: {str(rule)}", language="text")
    
    # Proof Steps
    if (st.session_state.config["show_steps"] and response.proof_result and 
        response.proof_result.steps):
        st.subheader("🔗 Formal Proof Steps")
        
        for i, step in enumerate(response.proof_result.steps, 1):
            with st.expander(f"Step {i}: Applied {step.rule_applied.name}"):
                st.markdown(f"**Premises:** {', '.join(str(p) for p in step.premises_used)}")
                st.markdown(f"**Conclusion:** {step.derived_fact}")
                st.markdown(f"**Rule:** {step.rule_applied.name}")
    
    # Natural Language Explanation
    st.subheader("📝 Mathematical Explanation")
    
    # Enhanced explanation display with proper LaTeX rendering
    display_mathematical_explanation_properly(response.explanation)
    
    # Additional details in expander
    with st.expander("🔧 Technical Details"):
        if response.proof_result:
            st.json({
                "goal_achieved": response.proof_result.goal_achieved,
                "iterations_used": response.proof_result.iterations_used,
                "time_elapsed": round(response.proof_result.time_elapsed, 4),
                "final_facts_count": len(response.proof_result.final_facts)
            })
        
        if response.metadata and "proof_statistics" in response.metadata:
            st.json(response.metadata["proof_statistics"])


def display_history():
    """Display problem solving history."""
    if not st.session_state.problem_history:
        return
    
    st.divider()
    st.header("📚 Problem History")
    
    for i, entry in enumerate(reversed(st.session_state.problem_history[-5:]), 1):
        with st.expander(f"Problem {len(st.session_state.problem_history) - i + 1}: {entry['problem'][:50]}..."):
            st.markdown(f"**Problem:** {entry['problem']}")
            
            response = entry['response']
            if response.success and response.proof_result and response.proof_result.goal_achieved:
                st.success("✅ Solved")
            else:
                st.warning("⚠️ Incomplete/Failed")
            
            if response.metadata:
                st.markdown(f"**Type:** {response.metadata.get('problem_type', 'unknown')}")
                st.markdown(f"**Time:** {response.metadata.get('processing_time', 0):.2f}s")
            
            st.markdown(f"**Explanation:** {response.explanation[:200]}...")


def display_system_stats():
    """Display system statistics."""
    if len(st.session_state.problem_history) > 0:
        st.divider()
        st.header("📈 Session Statistics")
        
        # Calculate stats
        total_problems = len(st.session_state.problem_history)
        successful = sum(1 for entry in st.session_state.problem_history 
                        if entry['response'].success and 
                        entry['response'].proof_result and 
                        entry['response'].proof_result.goal_achieved)
        
        avg_time = sum(entry['response'].metadata.get('processing_time', 0) 
                      for entry in st.session_state.problem_history 
                      if entry['response'].metadata) / max(1, total_problems)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Problems Attempted", total_problems)
        
        with col2:
            st.metric("Successfully Solved", successful)
        
        with col3:
            st.metric("Success Rate", f"{(successful/max(1,total_problems)):.1%}")
        
        st.metric("Average Processing Time", f"{avg_time:.2f}s")


def main():
    """Main application function."""
    initialize_session_state()
    display_header()
    display_sidebar()
    display_main_interface()
    display_results()
    display_history()
    display_system_stats()
    
    # Footer
    st.divider()
    st.markdown("""
    ---
    **MathGraph v1.0** | Hybrid Mathematical Reasoning System  
    *Combining LLMs with Formal Logic for Rigorous Mathematical Problem Solving*
    
    🔗 Built with: Python, Azure OpenAI GPT-4o, SymPy, NetworkX, Streamlit  
    🧠 Architecture: Natural Language ↔ Formal Logic ↔ Proof Engine ↔ Explanation
    """)


if __name__ == "__main__":
    main()