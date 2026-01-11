import argparse
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes import auditor_node, fixer_node, judge_node

# Load environment variables
load_dotenv()


def should_continue(state: AgentState) -> str:
    # Success case - all tests passed
    if state['status'] == "SUCCESS":
        print(f"🎉 SUCCESS: {state['file_name']} fixed in {state['iteration']} iteration(s)!")
        return "end"
    
    # Fail-safe: Max iterations reached
    if state['iteration'] >= 10:
        print(f"⚠️ FAIL-SAFE: Max iterations (10) reached for {state['file_name']}")
        print(f"   Final status: {state['status']}")
        return "end"
    
    # Continue - loop back to fixer
    print(f"🔄 RETRY: Iteration {state['iteration']}/10 - Looping back to Fixer...")
    return "continue"


def build_graph() -> StateGraph:
    """
    Builds the LangGraph workflow for the Refactoring Swarm.
    
    Graph Structure:
        START -> auditor -> fixer -> judge -> [conditional]
                                       ^         |
                                       |         v
                                       +---- (continue)
                                             (end) -> END
    """
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("auditor", auditor_node)
    workflow.add_node("fixer", fixer_node)
    workflow.add_node("judge", judge_node)
    
    
    workflow.set_entry_point("auditor")
    
    
    workflow.add_edge("auditor", "fixer")
    workflow.add_edge("fixer", "judge")
    
    
    workflow.add_conditional_edges(
        "judge",
        should_continue,
        {
            "continue": "fixer",  # Loop back to fixer
            "end": END            # Terminate the workflow
        }
    )
    
    # Compile the graph
    return workflow.compile()


def find_python_files(target_dir: str) -> list[str]:
    """
    Finds all Python files in the target directory.
    
    Args:
        target_dir: Directory to search
    
    Returns:
        List of Python file names (not full paths)
    """
    target_path = Path(target_dir)
    python_files = []
    
    for file in target_path.glob("*.py"):
        if file.is_file():
            python_files.append(file.name)
    
    return python_files


def main():
    """
    Main orchestration function for the Refactoring Swarm.
    """
    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Refactoring Swarm - Autonomous Python Code Fixer"
    )
    parser.add_argument(
        "--target_dir",
        type=str,
        required=True,
        help="Directory containing Python files to refactor"
    )
    args = parser.parse_args()
    
    # Validate environment
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ ERROR: GOOGLE_API_KEY environment variable not set!")
        print("   Please set it in your .env file or environment.")
        sys.exit(1)
    
    # Validate target directory
    if not os.path.exists(args.target_dir):
        print(f"❌ ERROR: Directory '{args.target_dir}' not found!")
        sys.exit(1)
    
    print("\n" + "="*70)
    print("🧬 REFACTORING SWARM - MULTI-AGENT CODE FIXER")
    print("="*70)
    print(f"📁 Target Directory: {args.target_dir}")
    print("🤖 Agents: Auditor -> Fixer -> Judge")
    print("🔄 Self-Healing: Max 10 iterations per file")
    print("="*70 + "\n")
    
    # Build the graph 
    print("🔨 Building LangGraph workflow...")
    try:
        graph = build_graph()
        print("✅ Graph compiled successfully!")
    except Exception as e:
        print(f"❌ Graph compilation failed: {e}")
        sys.exit(1)

    # Find Python files 
    python_files = find_python_files(args.target_dir)
    
    if not python_files:
        print(f"⚠️ No Python files found in {args.target_dir}")
        sys.exit(0)
    
    print(f"📝 Found {len(python_files)} Python file(s):")
    for file in python_files:
        print(f"   - {file}")
    print()

    print("⏳ PENDING: Agent execution loop implementation.")


if __name__ == "__main__":
    main()