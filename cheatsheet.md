# LangGraph Cheat Sheet

Quick reference for building your agent. Keep this open while you code.

---

## Imports

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
```

## Define State

```python
class AgentState(TypedDict):
    query: str
    result: str
    iteration_count: int
```

State is a `TypedDict`. Every node reads from it and returns a dict of fields to update.

## Define a Tool

```python
@tool
def my_tool(input_text: str) -> str:
    """This docstring is what the LLM sees. Make it clear."""
    return f"Result: {input_text}"
```

The `@tool` decorator comes from `langchain_core.tools`. The docstring matters — the LLM uses it to decide when to call the tool.

## Create the LLM

```python
# OpenAI
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Anthropic
llm = ChatAnthropic(model="claude-sonnet-4-20250514", temperature=0)
```

## Call the LLM

```python
messages = [
    SystemMessage(content="You are a helpful assistant."),
    HumanMessage(content="Analyze this text: ...")
]
response = llm.invoke(messages)
text = response.content  # <-- the string you want
```

## Write a Node

```python
def my_node(state: AgentState) -> dict:
    """Nodes take state, return a dict of updates."""
    # Do work using state["field_name"]
    result = some_logic(state["query"])
    # Return only the fields you want to update
    return {"result": result, "iteration_count": state["iteration_count"] + 1}
```

## Write a Routing Function

```python
def should_continue(state: AgentState) -> str:
    """Returns the NAME of the next node as a string."""
    if state["iteration_count"] >= 3:
        return "finalize"       # safety valve
    if "PASS" in state["evaluation"]:
        return "finalize"       # quality met
    return "work"               # loop back
```

## Build the Graph

```python
builder = StateGraph(AgentState)

# Add nodes (name, function)
builder.add_node("work", work_node)
builder.add_node("evaluate", evaluate_node)
builder.add_node("finalize", finalize_node)

# Add edges
builder.add_edge(START, "work")              # entry point
builder.add_edge("work", "evaluate")         # always goes work → evaluate
builder.add_edge("finalize", END)            # exit point

# Add conditional edge (the loop)
builder.add_conditional_edges(
    "evaluate",                               # from this node
    should_continue,                          # routing function
    ["work", "finalize"]                      # possible destinations
)

# Compile
graph = builder.compile()
```

## Run the Graph

```python
result = graph.invoke({
    "query": "your input here",
    "result": "",
    "iteration_count": 0
})

print(result["result"])
```

## Visualize the Graph

```python
# ASCII (no extra install needed)
graph.get_graph().print_ascii()

# PNG (requires: pip install pygraphviz)
graph.get_graph().draw_png("my_graph.png")
```

---

## Common Patterns

### Pattern 1: Evaluate-and-Retry Loop
```
START → work → evaluate → [good enough?]
                             ├── YES → finalize → END
                             └── NO  → work (loop)
```

### Pattern 2: Multi-Source Gatherer
```
START → gather_a → gather_b → combine → evaluate → [complete?]
                                                       ├── YES → END
                                                       └── NO  → gather_more
```

### Pattern 3: Classifier-Router
```
START → classify → [type?]
                     ├── A → handler_a ─┐
                     ├── B → handler_b ─┼── merge → END
                     └── C → handler_c ─┘
```

---

## Debugging

```python
# Print state inside any node
def my_node(state: AgentState) -> dict:
    print(f"--- MY_NODE ---")
    print(f"  input: {state['query'][:100]}")
    print(f"  iteration: {state['iteration_count']}")
    # ... your logic ...
    return updates

# Test a node in isolation
fake_state = {"query": "test", "result": "", "iteration_count": 0}
output = my_node(fake_state)
print(output)

# Test a tool in isolation
result = my_tool.invoke({"input_text": "test"})
print(result)
```
