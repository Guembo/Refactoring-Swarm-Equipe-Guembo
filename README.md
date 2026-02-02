# 🧬 Refactoring Swarm - Multi-Agent Code Fixer

An autonomous multi-agent system built with **LangGraph** that automatically fixes buggy Python code using AI-powered analysis, refactoring, and validation.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   REFACTORING SWARM                      │
│                                                          │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐     │
│  │          │      │          │      │          │     │
│  │ AUDITOR  │─────▶│  FIXER   │─────▶│  JUDGE   │     │
│  │          │      │          │      │          │     │
│  └──────────┘      └──────────┘      └──────────┘     │
│                           ▲                │            │
│                           │                │            │
│                           │  (iteration    │ (success   │
│                           │   < 10)        │  or max)   │
│                           │                ▼            │
│                           └────────────── END           │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Agent Workflow

1. **Auditor Agent** 🔍
   - Analyzes code for bugs, style issues, and missing type hints
   - Runs pylint static analysis
   - Generates structured refactoring plan
   - Logs with `ActionType.ANALYSIS`

2. **Fixer Agent** 🔧
   - Receives audit plan and previous test failures
   - Generates complete corrected code
   - Writes fixes to `sandbox/fixed_*.py` files
   - Logs with `ActionType.FIX`

3. **Judge Agent** ⚖️
   - Runs pytest test suite (if available)
   - **Gracefully handles missing test files** - exits with SUCCESS and note instead of failing
   - Validates pylint score (≥7.0)
   - Determines success/failure
   - Logs with `ActionType.DEBUG`

### Self-Healing Loop

- If tests fail, the workflow loops back to the **Fixer** agent
- Maximum of **10 iterations** to prevent infinite loops
- Each iteration includes previous test failure context

## 📁 Project Structure

```
Refactoring-Swarm/
├── main.py                  # Orchestrator (LangGraph workflow)
├── src/
│   ├── state.py            # AgentState TypedDict
│   ├── prompts.py          # System prompts for agents
│   ├── nodes.py            # Agent node implementations
│   ├── tools.py            # File I/O and subprocess wrappers
│   └── utils/
│       └── logger.py       # Experiment logging
├── sandbox/
│   ├── calculator.py       # Sample buggy code
│   ├── test_calculator.py  # Test suite
│   └── fixed_*.py          # Generated fixed files
├── logs/
│   └── experiment_data.json  # LLM interaction logs
├── requirements.txt
└── README.md
```

## 🚀 Installation

### 1. Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key_here
```

## 📋 Usage

### Basic Usage

```bash
python main.py --target_dir sandbox
```

This will:
1. Find all `.py` files in the `sandbox` directory
2. Run the refactoring workflow for each file
3. Write fixed code to `sandbox/fixed_*.py` files
4. Generate logs in `logs/experiment_data.json`

### Expected Output

```
🧬 REFACTORING SWARM - MULTI-AGENT CODE FIXER
==================================================================
📁 Target Directory: sandbox
🤖 Agents: Auditor -> Fixer -> Judge
🔄 Self-Healing: Max 10 iterations per file
==================================================================

📝 Found 1 Python file(s):
   - calculator.py

🔨 Building LangGraph workflow...
✅ Graph compiled successfully!

####################################################################
# Processing File 1/1: calculator.py
####################################################################

============================================================
🔍 AUDITOR: Analyzing calculator.py
============================================================
📊 Running pylint analysis...
🤖 Calling Gemini for code analysis...
✅ Auditor analysis complete

============================================================
🔧 FIXER: Applying fixes (Iteration 1/10)
============================================================
🤖 Calling Gemini to generate fixed code...
💾 Writing fixed code to sandbox/fixed_calculator.py...
✅ Fixer complete (Iteration 1)

============================================================
⚖️ JUDGE: Validating fixes for calculator.py
============================================================
🧪 Running pytest on test_calculator.py...
📊 Running pylint on calculator.py...
✅ VERDICT: All tests passed and code quality is acceptable!

🎉 SUCCESS: calculator.py fixed in 1 iteration(s)!

============================================================

📊 FINAL RESULTS
==================================================================
✅ calculator.py: SUCCESS (Iterations: 1)

==================================================================
✅ Success: 1/1
❌ Failed:  0/1
==================================================================

🔬 Check logs/experiment_data.json for detailed LLM interaction logs.

✨ REFACTORING SWARM COMPLETE!
```

## 🔬 Logging System

All LLM interactions are logged to `logs/experiment_data.json` with the following structure:

```json
{
  "id": "unique-uuid",
  "timestamp": "2026-01-06T03:30:00",
  "agent": "Auditor",
  "model": "gemini-2.5-flash",
  "action": "CODE_ANALYSIS",
  "details": {
    "input_prompt": "...",
    "output_response": "...",
    "file_analyzed": "calculator.py",
    "pylint_score": 8.5
  },
  "status": "SUCCESS"
}
```

### Action Types

- `CODE_ANALYSIS`: Auditor analyzing code
- `FIX`: Fixer generating corrected code
- `DEBUG`: Judge validating fixes

## 🧪 Testing

### Create Your Own Test Case

1. Create a buggy Python file in a test directory
2. Create a corresponding test file (`test_*.py` or `*_test.py`)
3. Run the swarm: `python main.py --target_dir your_test_dir`

### Example Test Structure

```python
# buggy_module.py
def divide(a, b):
    return a / b  # Bug: no zero check

# test_buggy_module.py
import pytest
from buggy_module import divide

def test_divide_zero():
    with pytest.raises(ZeroDivisionError):
        divide(5, 0)
```

## 🛠️ Technical Details

### Dependencies

- **LangGraph**: Workflow orchestration
- **LangChain**: LLM integration
- **Google Gemini**: LLM model (gemini-2.5-flash)
- **Pylint**: Static code analysis
- **Pytest**: Test execution
- **Python-dotenv**: Environment management

### Security Features

- **Sandbox validation**: All file operations validated within project directory
- **Path traversal prevention**: Absolute path resolution with security checks
- **Subprocess isolation**: Uses virtual environment's Python executable

### Constraints

- Max 10 iterations per file (fail-safe)
- Pylint score threshold: ≥7.0/10
- All tests must pass for success (if test file exists)
- **No test file required** - Judge exits gracefully with SUCCESS if test file missing
- Mandatory logging for all LLM interactions

## 📊 Performance

- **Average fix time**: 30-60 seconds per file (depending on LLM latency)
- **Success rate**: Depends on code complexity and test coverage
- **Token efficiency**: Uses structured prompts to minimize context

## 🐛 Troubleshooting

### "GOOGLE_API_KEY not found"

Ensure you have created a `.env` file with your API key:
```bash
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### "pylint is not installed"

Reinstall requirements:
```bash
pip install -r requirements.txt
```

### "No Python files found"

Check that your target directory contains `.py` files:
```bash
ls your_directory/*.py
```

## 📝 License

This project is for educational purposes.

## 🙏 Acknowledgments

Built with:
- LangGraph by LangChain
- Google Gemini AI
- Python ecosystem tools

---


