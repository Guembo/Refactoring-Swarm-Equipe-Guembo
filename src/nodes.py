"""
Agent Nodes for Refactoring Swarm
Implements the three main agents: Auditor, Fixer, and Judge.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI

from src.state import AgentState
from src.prompts import (
    AUDITOR_PROMPT,
    build_auditor_input
)
from src.utils.logger import log_experiment, ActionType
from src import tools

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _extract_pylint_score(pylint_output: str) -> float | None:
    """Extracts the pylint score from the output."""
    try:
        if "rated at" in pylint_output:
            parts = pylint_output.split("rated at")[1].split("/")[0]
            score = float(parts.strip())
            return score
    except (IndexError, ValueError):
        pass
    return None

# =============================================================================
# LLM Configuration
# =============================================================================

def get_llm(temperature: float = 0.3):
    # ... (Same as Commit 1) ...
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("❌ GOOGLE_API_KEY not found")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=temperature,
        google_api_key=api_key,
        convert_system_message_to_human=True
    )

# =============================================================================
# AUDITOR NODE
# =============================================================================

def auditor_node(state: AgentState) -> AgentState:
    """Auditor Agent: Analyzes code for bugs, style issues, and missing types."""
    print(f"\n{'='*60}")
    print(f"🔍 AUDITOR: Analyzing {state['file_name']}")
    print(f"{'='*60}\n")
    
    file_path = os.path.join(state['target_dir'], state['file_name'])
    try:
        code_content = tools.read_file(file_path)
        state['code_content'] = code_content
    except Exception as e:
        print(f"❌ Failed to read file: {str(e)}")
        state['status'] = "FAILED"
        return state
    
    print("📊 Running pylint analysis...")
    pylint_report = tools.run_pylint(file_path)
    state['pylint_report'] = pylint_report
    
    input_prompt = build_auditor_input(
        code_content=code_content,
        pylint_report=pylint_report,
        file_name=state['file_name']
    )
    
    print("🤖 Calling Gemini for code analysis...")
    try:
        llm = get_llm(temperature=0.3)
        messages = [("system", AUDITOR_PROMPT), ("user", input_prompt)]
        response = llm.invoke(messages)
        output_response = response.content
        
        log_experiment(
            agent_name="Auditor",
            model_used="gemini-2.5-flash-lite",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": input_prompt,
                "output_response": output_response,
                "file_analyzed": state['file_name'],
                "pylint_score": _extract_pylint_score(pylint_report)
            },
            status="SUCCESS"
        )
        
        state['refactoring_plan'] = output_response
        print("✅ Auditor analysis complete\n")
        
    except Exception as e:
        print(f"❌ LLM call failed: {str(e)}")
        state['status'] = "FAILED"
    
    return state

# Stubs for others
def fixer_node(state: AgentState) -> AgentState: pass
def judge_node(state: AgentState) -> AgentState: pass