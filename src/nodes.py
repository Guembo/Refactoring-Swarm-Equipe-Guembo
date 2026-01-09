"""
Agent Nodes for Refactoring Swarm
Implements the three main agents: Auditor, Fixer, and Judge.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI

from src.state import AgentState
from src.utils.logger import log_experiment, ActionType
from src import tools

# Placeholder imports until prompts are ready
# from src.prompts import AUDITOR_PROMPT, FIXER_PROMPT, build_auditor_input, build_fixer_input

# =============================================================================
# LLM Configuration
# =============================================================================

def get_llm(temperature: float = 0.3):
    """
    Initialize and return the Gemini LLM instance.
    Args:
        temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
    Returns:
        ChatGoogleGenerativeAI instance
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "❌ GOOGLE_API_KEY not found in environment variables. "
            "Please set it before running the agents."
        )
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=temperature,
        google_api_key=api_key,
        convert_system_message_to_human=True
    )

# =============================================================================
# AGENT NODES STUBS
# =============================================================================

def auditor_node(state: AgentState) -> AgentState:
    """Auditor Agent Stub"""
    print("Auditor node not implemented yet")
    return state

def fixer_node(state: AgentState) -> AgentState:
    """Fixer Agent Stub"""
    print("Fixer node not implemented yet")
    return state

def judge_node(state: AgentState) -> AgentState:
    """Judge Agent Stub"""
    print("Judge node not implemented yet")
    return state