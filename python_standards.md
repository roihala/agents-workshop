# Python Standards Reference

> Real-world Python patterns from a production trading system. Use these as a reference for writing clean, well-structured agent code.

---

## Error Handling

### Strategy: Fail Fast on Critical, Degrade on Non-Critical

```python
from enum import Enum

class ErrorSeverity(Enum):
    CRITICAL = "critical"  # Must halt execution
    HIGH = "high"          # Data integrity risk
    MEDIUM = "medium"      # Can degrade gracefully
    LOW = "low"            # Log and continue

# Critical operations — always fail fast
def validate_input(data: dict) -> None:
    if not data.get("query"):
        raise ValueError("Missing required field: query")

# Non-critical — degrade gracefully
def fetch_optional_context(query: str) -> str:
    try:
        return search_web(query)
    except Exception as e:
        print(f"Warning: web search failed, continuing without it: {e}")
        return ""
```

**For your workshop agent:** Use fail-fast for input validation. Use try/except with fallbacks for tool calls that might fail.

---

## Type Hints

### Always Type Your Functions

```python
from typing import TypedDict, Optional
from dataclasses import dataclass

# State definition (you're already doing this with TypedDict)
class AgentState(TypedDict):
    query: str
    results: list[str]
    iteration_count: int

# Return types for complex results
@dataclass
class EvaluationResult:
    passed: bool
    reason: str
    confidence: float

def evaluate_output(output: str, criteria: str) -> EvaluationResult:
    # ... evaluation logic ...
    return EvaluationResult(passed=True, reason="Meets criteria", confidence=0.9)
```

**For your workshop agent:** Type your node functions and tool return values. It makes debugging much easier.

---

## File Organization

### One Responsibility Per File

```
my_agent/
├── agent.py            # Graph definition and main entry point
├── state.py            # State TypedDict (if complex)
├── nodes.py            # Node functions
├── tools.py            # Tool definitions
├── prompts.py          # System prompts as constants
└── test_data/          # Mock data for testing
```

**For your workshop agent:** Keeping everything in one `agent.py` is fine for the workshop. But if your file gets past ~200 lines, consider splitting nodes and tools into separate files.

---

## Return Types

### Prefer Typed Returns Over Dicts

```python
# Avoid: untyped dict returns
def analyze(text: str) -> dict:
    return {"score": 0.8, "label": "positive", "confidence": 0.9}

# Prefer: typed dataclass returns
@dataclass
class AnalysisResult:
    score: float
    label: str
    confidence: float

def analyze(text: str) -> AnalysisResult:
    return AnalysisResult(score=0.8, label="positive", confidence=0.9)
```

---

## Logging

### Print Statements Are Fine for the Workshop

In production you'd use structured logging. For the workshop, `print` with clear labels is perfectly fine:

```python
def work_node(state: AgentState) -> dict:
    print(f"\n--- WORK NODE (iteration {state['iteration_count']}) ---")
    print(f"  Input: {state['query'][:80]}...")

    # ... do work ...

    print(f"  Output: {result[:80]}...")
    return {"result": result}
```

The key is to print at every node so you can see what's happening when you run the agent.

---

## Constants and Configuration

### Don't Hardcode Strings

```python
# Avoid: magic strings scattered through code
if "PASS" in evaluation:
    return "finalize"

# Prefer: named constants
EVAL_PASS = "PASS"
EVAL_FAIL = "FAIL"
MAX_ITERATIONS = 3

if EVAL_PASS in evaluation:
    return "finalize"
```

---

## Retry Logic

### Simple Retry for Flaky Operations

```python
import time

def retry(func, max_attempts: int = 3, backoff: float = 1.0):
    """Retry a function with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            wait = backoff * (2 ** attempt)
            print(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait}s...")
            time.sleep(wait)
```

**For your workshop agent:** Wrap LLM calls in retry logic if you're hitting rate limits.
