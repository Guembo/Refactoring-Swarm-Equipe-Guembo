"""
Graph State Definition
Defines the state structure shared across all agents in the LangGraph workflow.
"""

from typing import TypedDict, Literal


class AgentState(TypedDict):
    """
    State container for the Refactoring Swarm workflow.
    
    This state is passed between agents and tracks all necessary information
    for the code refactoring process.
    """
    # Input configuration
    target_dir: str  # Directory containing the files to refactor
    file_name: str   # Name of the file currently being fixed
    
    # Code and analysis
    code_content: str       # Current version of the code being refactored
    refactoring_plan: str   # Auditor's structured analysis and recommendations
    fixed_file_path: str    # Path to fixed code in sandbox folder (set by fixer)
    
    # Testing and validation results
    test_results: str   # Output from pytest execution
    pylint_report: str  # Output from pylint analysis
    
    # Flow control
    iteration: int  # Current iteration count (for self-healing loop, max 10)
    status: Literal["IN_PROGRESS", "SUCCESS", "FAILED"]  # Overall workflow status
