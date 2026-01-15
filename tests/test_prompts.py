import pytest
from src.prompts import build_auditor_input, build_fixer_input


# =============================================================================
# Tests for build_auditor_input
# =============================================================================

def test_build_auditor_input_basic():
    """Test basic functionality with typical inputs."""
    code_content = "def add(a, b):\n    return a + b"
    pylint_report = "No issues found"
    file_name = "calculator.py"
    
    result = build_auditor_input(code_content, pylint_report, file_name)
    
    # Verify all components are present in the output
    assert "**File:** calculator.py" in result
    assert "**Pylint Report:**" in result
    assert "No issues found" in result
    assert "**Code to Analyze:**" in result
    assert "```python" in result
    assert "def add(a, b):" in result
    assert "return a + b" in result
    assert "Please provide your structured analysis" in result


def test_build_auditor_input_with_multiline_code():
    """Test with multi-line code content."""
    code_content = """class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, x, y):
        return x + y"""
    
    pylint_report = "C0301: Line too long (85/80) (line-too-long)"
    file_name = "calculator_class.py"
    
    result = build_auditor_input(code_content, pylint_report, file_name)
    
    # Verify multiline code is preserved
    assert "class Calculator:" in result
    assert "def __init__(self):" in result
    assert "def add(self, x, y):" in result
    assert file_name in result
    assert pylint_report in result


def test_build_auditor_input_with_complex_pylint_report():
    """Test with a detailed pylint report."""
    code_content = "x = 1"
    pylint_report = """************* Module test
test.py:1:0: C0114: Missing module docstring (missing-module-docstring)
test.py:1:0: C0103: Constant name "x" doesn't conform to UPPER_CASE naming style (invalid-name)

------------------------------------------------------------------
Your code has been rated at 0.00/10"""
    
    file_name = "test.py"
    
    result = build_auditor_input(code_content, pylint_report, file_name)
    
    # Verify complex pylint report is included
    assert "missing-module-docstring" in result
    assert "invalid-name" in result
    assert "Your code has been rated at 0.00/10" in result
    assert file_name in result


def test_build_auditor_input_empty_pylint_report():
    """Test with an empty pylint report."""
    code_content = "# Perfect code"
    pylint_report = ""
    file_name = "perfect.py"
    
    result = build_auditor_input(code_content, pylint_report, file_name)
    
    # Verify structure is maintained even with empty report
    assert "**File:** perfect.py" in result
    assert "**Pylint Report:**" in result
    assert "**Code to Analyze:**" in result
    assert "# Perfect code" in result


def test_build_auditor_input_special_characters():
    """Test with special characters in inputs."""
    code_content = 'print("Hello, \\n world!")\ndata = {"key": "value"}'
    pylint_report = "W0301: Unnecessary semicolon (unnecessary-semicolon)"
    file_name = "special_chars.py"
    
    result = build_auditor_input(code_content, pylint_report, file_name)
    
    # Verify special characters are preserved
    assert 'print("Hello, \\n world!")' in result
    assert '{"key": "value"}' in result
    assert file_name in result


def test_build_auditor_input_return_type():
    """Test that the function returns a string."""
    result = build_auditor_input("code", "report", "file.py")
    assert isinstance(result, str)


def test_build_auditor_input_non_empty():
    """Test that the function always returns a non-empty string."""
    result = build_auditor_input("", "", "")
    assert len(result) > 0
    assert "**File:**" in result


def test_build_auditor_input_formatting():
    """Test the exact formatting of the output."""
    code_content = "x = 1"
    pylint_report = "All good"
    file_name = "test.py"
    
    result = build_auditor_input(code_content, pylint_report, file_name)
    
    # Test that markdown code blocks are properly formatted
    assert result.count("```") == 4  # 2 opening + 2 closing backticks
    assert "```python" in result
    
    # Verify the structure order
    file_index = result.index("**File:**")
    pylint_index = result.index("**Pylint Report:**")
    code_index = result.index("**Code to Analyze:**")
    
    assert file_index < pylint_index < code_index


# =============================================================================
# Tests for build_fixer_input
# =============================================================================

def test_build_fixer_input_first_iteration():
    """Test build_fixer_input with iteration 1 (no test results section)."""
    code_content = "def add(a, b):\n    return a + b"
    refactoring_plan = "No issues found, code looks good."
    test_results = "All tests passed"
    pylint_report = "Your code has been rated at 10.00/10"
    iteration = 1
    file_name = "calculator.py"
    
    result = build_fixer_input(
        code_content, refactoring_plan, test_results, 
        pylint_report, iteration, file_name
    )
    
    # Verify all base components are present
    assert "**File:** calculator.py" in result
    assert "**Iteration:** 1/10" in result
    assert "**Original Code:**" in result
    assert "```python" in result
    assert "def add(a, b):" in result
    assert "**Refactoring Plan from Auditor:**" in result
    assert "No issues found" in result
    assert "**Pylint Report:**" in result
    assert "Your code has been rated at 10.00/10" in result
    assert "Provide the COMPLETE corrected code now." in result
    
    # Test results should NOT be included for iteration 1
    assert "**Previous Test Results (FAILURES TO FIX):**" not in result
    assert "⚠️ **IMPORTANT:**" not in result


def test_build_fixer_input_retry_with_test_results():
    """Test build_fixer_input with iteration > 1 and test results."""
    code_content = "def subtract(a, b):\n    return a + b  # BUG"
    refactoring_plan = "Fix the subtract function to use subtraction."
    test_results = "FAILED test_calculator.py::test_subtract - AssertionError"
    pylint_report = "No issues found"
    iteration = 3
    file_name = "calculator.py"
    
    result = build_fixer_input(
        code_content, refactoring_plan, test_results,
        pylint_report, iteration, file_name
    )
    
    # Verify iteration counter
    assert "**Iteration:** 3/10" in result
    
    # Verify test results section IS included
    assert "**Previous Test Results (FAILURES TO FIX):**" in result
    assert "FAILED test_calculator.py::test_subtract" in result
    assert "⚠️ **IMPORTANT:**" in result
    assert "This is attempt #3" in result
    assert "The previous fix attempt failed the tests above" in result
    assert "Do not repeat the same mistakes" in result


def test_build_fixer_input_retry_without_test_results():
    """Test build_fixer_input with iteration > 1 but empty test results."""
    code_content = "x = 1"
    refactoring_plan = "Add docstring"
    test_results = ""  # Empty test results
    pylint_report = "Missing docstring"
    iteration = 2
    file_name = "module.py"
    
    result = build_fixer_input(
        code_content, refactoring_plan, test_results,
        pylint_report, iteration, file_name
    )
    
    # Test results section should NOT be included (empty test_results)
    assert "**Previous Test Results (FAILURES TO FIX):**" not in result
    assert "⚠️ **IMPORTANT:**" not in result


def test_build_fixer_input_multiline_code():
    """Test with multi-line code content."""
    code_content = """class Calculator:
    def __init__(self):
        self.result = 0
    
    def add(self, x, y):
        return x + y"""
    
    refactoring_plan = "Add type hints and docstrings"
    test_results = ""
    pylint_report = "C0114: Missing module docstring"
    iteration = 1
    file_name = "calculator.py"
    
    result = build_fixer_input(
        code_content, refactoring_plan, test_results,
        pylint_report, iteration, file_name
    )
    
    # Verify multiline code is preserved
    assert "class Calculator:" in result
    assert "def __init__(self):" in result
    assert "def add(self, x, y):" in result


def test_build_fixer_input_complex_test_failures():
    """Test with detailed test failure output."""
    code_content = "def divide(a, b):\n    return a / b"
    refactoring_plan = "Add zero division check"
    test_results = """============================= FAILURES ==============================
_______ test_divide_by_zero _______

    def test_divide_by_zero():
>       result = divide(10, 0)
E       ZeroDivisionError: division by zero

test_calculator.py:15: ZeroDivisionError
===================== 1 failed in 0.05s ======================"""
    
    pylint_report = "No issues found"
    iteration = 2
    file_name = "math_utils.py"
    
    result = build_fixer_input(
        code_content, refactoring_plan, test_results,
        pylint_report, iteration, file_name
    )
    
    # Verify complex test failure is included
    assert "ZeroDivisionError: division by zero" in result
    assert "test_calculator.py:15" in result
    assert "1 failed in 0.05s" in result
    assert "This is attempt #2" in result


def test_build_fixer_input_max_iteration():
    """Test with maximum iteration number."""
    result = build_fixer_input(
        code_content="x = 1",
        refactoring_plan="Fix naming",
        test_results="Some failures",
        pylint_report="C0103: Invalid name",
        iteration=10,
        file_name="test.py"
    )
    
    assert "**Iteration:** 10/10" in result
    assert "This is attempt #10" in result


def test_build_fixer_input_return_type():
    """Test that the function returns a string."""
    result = build_fixer_input(
        code_content="code",
        refactoring_plan="plan",
        test_results="",
        pylint_report="report",
        iteration=1,
        file_name="file.py"
    )
    assert isinstance(result, str)


def test_build_fixer_input_non_empty():
    """Test that the function always returns a non-empty string."""
    result = build_fixer_input(
        code_content="",
        refactoring_plan="",
        test_results="",
        pylint_report="",
        iteration=1,
        file_name=""
    )
    assert len(result) > 0
    assert "**File:**" in result
    assert "**Iteration:**" in result


def test_build_fixer_input_formatting():
    """Test the exact formatting and structure of the output."""
    code_content = "x = 1"
    refactoring_plan = "Improve naming"
    test_results = ""
    pylint_report = "All good"
    iteration = 1
    file_name = "test.py"
    
    result = build_fixer_input(
        code_content, refactoring_plan, test_results,
        pylint_report, iteration, file_name
    )
    
    # Verify markdown code blocks for main sections
    assert "```python" in result
    assert result.count("```") >= 4  # At least 2 code blocks
    
    # Verify the structure order
    file_index = result.index("**File:**")
    iteration_index = result.index("**Iteration:**")
    code_index = result.index("**Original Code:**")
    plan_index = result.index("**Refactoring Plan from Auditor:**")
    pylint_index = result.index("**Pylint Report:**")
    complete_index = result.index("Provide the COMPLETE corrected code now.")
    
    assert file_index < iteration_index < code_index < plan_index < pylint_index < complete_index


def test_build_fixer_input_special_characters():
    """Test with special characters in inputs."""
    code_content = 'print("Hello\\nWorld")\ndata = {"key": "value"}'
    refactoring_plan = "Refactor to use f-strings"
    test_results = 'AssertionError: Expected "Hello" but got "Hello\\nWorld"'
    pylint_report = "W0301: Unnecessary semicolon"
    iteration = 2
    file_name = "string_utils.py"
    
    result = build_fixer_input(
        code_content, refactoring_plan, test_results,
        pylint_report, iteration, file_name
    )
    
    # Verify special characters are preserved
    assert 'print("Hello\\nWorld")' in result
    assert '{"key": "value"}' in result
    assert 'Expected "Hello"' in result


def test_build_fixer_input_conditional_test_results_none():
    """Test that None test_results is handled like empty string."""
    result = build_fixer_input(
        code_content="x = 1",
        refactoring_plan="plan",
        test_results=None,
        pylint_report="report",
        iteration=5,
        file_name="file.py"
    )
    
    # Should not include test results section even though iteration > 1
    # because test_results is None (falsy)
    assert "**Previous Test Results (FAILURES TO FIX):**" not in result
