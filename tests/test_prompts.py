import pytest
from src.prompts import build_auditor_input


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
