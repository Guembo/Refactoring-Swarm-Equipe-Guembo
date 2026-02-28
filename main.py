"""
Refactoring Swarm - Main Orchestrator
Multi-agent system using LangGraph to automatically fix buggy Python code.

Architecture: Auditor -> Fixer -> Judge (with self-healing loop)
"""

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
    
    Determines whether to:
    - END (success or max iterations reached)
    - Loop back to Fixer (for another attempt)
    
    Args:
        state: Current agent state
    
    Returns:
        "end" or "continue" (routing decision)
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
    
    Graph Structure:
        START -> auditor -> fixer -> judge -> [conditional]
                                       ^         |
                                       |         v
                                       +---- (continue)
                                             (end) -> END
    
    Returns:
        Compiled StateGraph
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


from pathlib import Path

from pathlib import Path

def find_python_files(target_dir: str) -> list[str]:
    """
    Finds all Python files recursively in the target directory.
    
    Args:
        target_dir: Directory to search
    
    Returns:
        List of Python file paths relative to the target directory
    """
    target_path = Path(target_dir)
    python_files = []
    
    for file in target_path.rglob("*.py"):
        if file.is_file():
            relative_path = file.relative_to(target_path)
            python_files.append(str(relative_path))
            
    return python_files
def main():
    """
    Main orchestration function for the Refactoring Swarm.
    
    Workflow:
    1. Parse command-line arguments
    2. Validate target directory
    3. Find all Python files
    4. Build the LangGraph
    5. Execute the graph for each file
    6. Report results
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
    
    # Process each file
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
            final_state = graph.invoke(initial_state, config={"recursion_limit": 50})
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
    
    # Print final summary
    print("\n" + "="*70)
    print("📊 FINAL RESULTS")
    print("="*70)
    
    success_count = sum(1 for r in results if r["status"] == "SUCCESS")
    failed_count = sum(1 for r in results if r["status"] in ["FAILED", "ERROR"])
    
    for result in results:
        status_emoji = "✅" if result["status"] == "SUCCESS" else "❌"
        print(f"{status_emoji} {result['file']}: {result['status']} "
              f"(Iterations: {result['iterations']})")
    
    print("\n" + "="*70)
    print(f"✅ Success: {success_count}/{len(python_files)}")
    print(f"❌ Failed:  {failed_count}/{len(python_files)}")
    print("="*70)
    print("\n🔬 Check logs/experiment_data.json for detailed LLM interaction logs.")
    print("\n✨ REFACTORING SWARM COMPLETE!\n")


if __name__ == "__main__":
    main()
