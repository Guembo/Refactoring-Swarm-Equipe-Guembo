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
    """
    Conditional routing logic for the Judge node.
    """
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
    """
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("auditor", auditor_node)
    workflow.add_node("fixer", fixer_node)
    workflow.add_node("judge", judge_node)
    
    # Set entry point
    workflow.set_entry_point("auditor")
    
    # Add edges
    workflow.add_edge("auditor", "fixer")
    workflow.add_edge("fixer", "judge")
    
    # Add conditional edge from judge
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
    
    # Find Python files
    python_files = find_python_files(args.target_dir)
    
    if not python_files:
        print(f"⚠️ No Python files found in {args.target_dir}")
        sys.exit(0)
    
    print(f"📝 Found {len(python_files)} Python file(s):")
    for file in python_files:
        print(f"   - {file}")
    print()
    
    # Build the graph
    print("🔨 Building LangGraph workflow...")
    graph = build_graph()
    print("✅ Graph compiled successfully!\n")
    
    # Process each file (ADDED IN THIS COMMIT)
    results = []
    for i, file_name in enumerate(python_files, 1):
        print(f"\n{'#'*70}")
        print(f"# Processing File {i}/{len(python_files)}: {file_name}")
        print(f"{'#'*70}\n")
        
        # Initialize state
        initial_state: AgentState = {
            "target_dir": args.target_dir,
            "file_name": file_name,
            "code_content": "",
            "test_results": "",
            "pylint_report": "",
            "iteration": 0,
            "refactoring_plan": "",
            "status": "IN_PROGRESS"
        }
        
        # Run the graph
        try:
            final_state = graph.invoke(initial_state)
            results.append({
                "file": file_name,
                "status": final_state["status"],
                "iterations": final_state["iteration"]
            })
        except Exception as e:
            print(f"\n❌ ERROR processing {file_name}: {str(e)}")
            results.append({
                "file": file_name,
                "status": "ERROR",
                "iterations": 0,
                "error": str(e)
            })

    # Summary reporting will be added in the final commit...
    print("\n✅ Batch execution complete.")


if __name__ == "__main__":
    main()