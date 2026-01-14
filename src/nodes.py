"""
Agent Nodes for Refactoring Swarm
Implements the three main agents: Auditor, Fixer, and Judge.
"""

import os
from langchain_google_genai import ChatGoogleGenerativeAI

from src.state import AgentState
from src.prompts import (
    AUDITOR_PROMPT,
    FIXER_PROMPT,          # <--- Added
    build_auditor_input,
    build_fixer_input      # <--- Added
)
from src.utils.logger import log_experiment, ActionType
from src import tools


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
# HELPER FUNCTIONS
# =============================================================================

def _extract_code_from_response(response: str) -> str:
    """
    Extracts Python code from LLM response, handling markdown code blocks.
    
    Args:
        response: Raw LLM response
    
    Returns:
        Extracted code content
    """
    # Check if response contains markdown code block
    if "```python" in response:
        # Extract content between ```python and ```
        start = response.find("```python") + len("```python")
        end = response.find("```", start)
        if end != -1:
            return response[start:end].strip()
    elif "```" in response:
        # Generic code block
        start = response.find("```") + 3
        end = response.find("```", start)
        if end != -1:
            return response[start:end].strip()
    
    # If no code block found, return the entire response
    return response.strip()


def _extract_pylint_score(pylint_output: str) -> float | None:
    """
    Extracts the pylint score from the output.
    
    Args:
        pylint_output: Raw pylint output
    
    Returns:
        Pylint score as float, or None if not found
    """
    try:
        # Look for "Your code has been rated at X.XX/10"
        if "rated at" in pylint_output:
            parts = pylint_output.split("rated at")[1].split("/")[0]
            score = float(parts.strip())
            return score
    except (IndexError, ValueError):
        pass
    
    return None


# =============================================================================
# AUDITOR NODE
# =============================================================================

def auditor_node(state: AgentState) -> AgentState:
    """
    Auditor Agent: Analyzes code for bugs, style issues, and missing types.
    
    Workflow:
    1. Read the target file
    2. Run pylint analysis
    3. Send code + pylint report to LLM for analysis
    4. Log the interaction (ActionType.ANALYSIS)
    5. Update state with refactoring plan
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with refactoring_plan populated
    """
    print(f"\n{'='*60}")
    print(f"🔍 AUDITOR: Analyzing {state['file_name']}")
    print(f"{'='*60}\n")
    
    # Read the target file
    file_path = os.path.join(state['target_dir'], state['file_name'])
    try:
        code_content = tools.read_file(file_path)
        state['code_content'] = code_content
    except Exception as e:
        error_msg = f"Failed to read file: {str(e)}"
        print(f"❌ {error_msg}")
        state['status'] = "FAILED"
        return state
    
    # Run pylint analysis
    print("📊 Running pylint analysis...")
    pylint_report = tools.run_pylint(file_path)
    state['pylint_report'] = pylint_report
    
    # Build the input prompt
    input_prompt = build_auditor_input(
        code_content=code_content,
        pylint_report=pylint_report,
        file_name=state['file_name']
    )
    
    # Call the LLM
    print("🤖 Calling Gemini for code analysis...")
    try:
        llm = get_llm(temperature=0.3)
        messages = [
            ("system", AUDITOR_PROMPT),
            ("user", input_prompt)
        ]
        response = llm.invoke(messages)
        output_response = response.content
        
        # Log the interaction (MANDATORY)
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
        
        # Update state
        state['refactoring_plan'] = output_response
        print("✅ Auditor analysis complete\n")
        
    except Exception as e:
        error_msg = f"LLM call failed: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Log the failure
        log_experiment(
            agent_name="Auditor",
            model_used="gemini-2.5-flash-lite",
            action=ActionType.ANALYSIS,
            details={
                "input_prompt": input_prompt,
                "output_response": error_msg,
                "file_analyzed": state['file_name'],
                "error": str(e)
            },
            status="FAILURE"
        )
        
        state['status'] = "FAILED"
    
    return state


# =============================================================================
# FIXER NODE
# =============================================================================

def fixer_node(state: AgentState) -> AgentState:
    """
    Fixer Agent: Applies fixes based on the Auditor's plan and test failures.
    
    Workflow:
    1. Read refactoring plan, code, test results, pylint report
    2. Send all context to LLM for code generation
    3. Log the interaction (ActionType.FIX)
    4. Write the corrected code to file
    5. Increment iteration counter
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with incremented iteration and new code written
    """
    print(f"\n{'='*60}")
    print(f"🔧 FIXER: Applying fixes (Iteration {state['iteration'] + 1}/10)")
    print(f"{'='*60}\n")
    
    # Build the input prompt
    input_prompt = build_fixer_input(
        code_content=state['code_content'],
        refactoring_plan=state['refactoring_plan'],
        test_results=state.get('test_results', ''),
        pylint_report=state['pylint_report'],
        iteration=state['iteration'] + 1,
        file_name=state['file_name']
    )
    
    # Call the LLM
    print("🤖 Calling Gemini to generate fixed code...")
    try:
        llm = get_llm(temperature=0.2)  # Lower temperature for code generation
        messages = [
            ("system", FIXER_PROMPT),
            ("user", input_prompt)
        ]
        response = llm.invoke(messages)
        output_response = response.content
        
        # Extract code from markdown if present
        fixed_code = _extract_code_from_response(output_response)
        
        # Log the interaction (MANDATORY)
        log_experiment(
            agent_name="Fixer",
            model_used="gemini-2.5-flash-lite",
            action=ActionType.FIX,
            details={
                "input_prompt": input_prompt,
                "output_response": output_response,
                "file_fixed": state['file_name'],
                "iteration": state['iteration'] + 1,
                "code_length": len(fixed_code)
            },
            status="SUCCESS"
        )
        
        # Write the fixed code to file
        file_path = os.path.join(state['target_dir'], state['file_name'])
        print(f"💾 Writing fixed code to {state['file_name']}...")
        tools.write_file(file_path, fixed_code)
        
        # Update state
        state['code_content'] = fixed_code
        state['iteration'] += 1
        print(f"✅ Fixer complete (Iteration {state['iteration']})\n")
        
    except Exception as e:
        error_msg = f"LLM call or file write failed: {str(e)}"
        print(f"❌ {error_msg}")
        
        # Log the failure
        log_experiment(
            agent_name="Fixer",
            model_used="gemini-2.5-flash-lite",
            action=ActionType.FIX,
            details={
                "input_prompt": input_prompt,
                "output_response": error_msg,
                "file_fixed": state['file_name'],
                "iteration": state['iteration'] + 1,
                "error": str(e)
            },
            status="FAILURE"
        )
        
        state['status'] = "FAILED"
    
    return state


# =============================================================================
# JUDGE NODE
# =============================================================================

def judge_node(state: AgentState) -> AgentState:
    """
    Judge Agent: Validates the fixed code using pytest and pylint.
    
    Workflow:
    1. Run pytest on the corresponding test file
    2. Run pylint on the fixed code
    3. Analyze results to determine success/failure
    4. Log the validation (ActionType.DEBUG)
    5. Update status accordingly
    
    Args:
        state: Current agent state
    
    Returns:
        Updated state with test_results, pylint_report, and status
    """
    print(f"\n{'='*60}")
    print(f"⚖️ JUDGE: Validating fixes for {state['file_name']}")
    print(f"{'='*60}\n")
    
    file_path = os.path.join(state['target_dir'], state['file_name'])
    
    # Run pytest (assuming test file follows naming convention)
    test_file_name = state['file_name'].replace('.py', '_test.py')
    if not test_file_name.startswith('test_'):
        test_file_name = 'test_' + state['file_name']
    
    test_path = os.path.join(state['target_dir'], test_file_name)
    
    print(f"🧪 Running pytest on {test_file_name}...")
    test_results = tools.run_pytest(test_path)
    state['test_results'] = test_results
    
    # Run pylint
    print(f"📊 Running pylint on {state['file_name']}...")
    pylint_report = tools.run_pylint(file_path)
    state['pylint_report'] = pylint_report
    
    # Analyze results
    tests_passed = "✅ All tests passed!" in test_results or "passed" in test_results.lower()
    pylint_score = _extract_pylint_score(pylint_report)
    
    # Determine success (tests pass + reasonable pylint score)
    if tests_passed and (pylint_score is None or pylint_score >= 7.0):
        state['status'] = "SUCCESS"
        verdict = "SUCCESS"
        print("✅ VERDICT: All tests passed and code quality is acceptable!")
    else:
        state['status'] = "FAILED"
        verdict = "FAILED"
        if not tests_passed:
            print("❌ VERDICT: Tests failed")
        else:
            print(f"⚠️ VERDICT: Pylint score too low ({pylint_score}/10)")
    
    # Log the validation (MANDATORY)
    log_experiment(
        agent_name="Judge",
        model_used="gemini-2.5-flash-lite",  # Judge doesn't call LLM but we log for consistency
        action=ActionType.DEBUG,
        details={
            "input_prompt": f"Validating {state['file_name']} at iteration {state['iteration']}",
            "output_response": f"Tests passed: {tests_passed}, Pylint score: {pylint_score}",
            "test_results": test_results,
            "pylint_report": pylint_report,
            "file_validated": state['file_name'],
            "iteration": state['iteration'],
            "tests_passed": tests_passed,
            "pylint_score": pylint_score
        },
        status=verdict
    )
    
    print(f"\n{'='*60}\n")
    
    return state

