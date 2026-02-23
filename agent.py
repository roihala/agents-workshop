"""
Agent: [YOUR AGENT NAME]
Team: [YOUR NAMES]
Description: [ONE SENTENCE]
"""

from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END

# ── 1. TOOLS ──────────────────────────────────────────────

@tool
def example_tool(input_text: str) -> str:
    """Describe what this tool does. The LLM reads this docstring."""
    # Replace with your real tool logic
    return f"Processed: {input_text}"


# ── 2. STATE ──────────────────────────────────────────────

class AgentState(TypedDict):
    input: str              # What the user gives the agent
    intermediate: str       # Work-in-progress data
    evaluation: str         # How the agent judges its own work
    output: str             # The final result
    iteration_count: int    # Safety valve


# ── 3. MODEL ──────────────────────────────────────────────

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# ── 4. NODES ──────────────────────────────────────────────
# Each node is a function: takes state, returns a dict of state updates.

def work_node(state: AgentState) -> dict:
    """The main work step. Replace with your agent's core logic."""
    print(f"\n--- WORK NODE (iteration {state.get('iteration_count', 0)}) ---")
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content=f"Process this: {state['input']}")
    ]
    response = llm.invoke(messages)
    print(f"Output: {response.content[:100]}...")
    return {
        "intermediate": response.content,
        "iteration_count": state.get("iteration_count", 0) + 1
    }


def evaluate_node(state: AgentState) -> dict:
    """Evaluate the work and decide if it's good enough."""
    messages = [
        SystemMessage(content="Evaluate the following output. Respond with PASS or FAIL and a brief reason."),
        HumanMessage(content=f"Original request: {state['input']}\n\nOutput to evaluate:\n{state['intermediate']}")
    ]
    response = llm.invoke(messages)
    print(f"--- EVALUATION: {response.content[:100]}...")
    return {"evaluation": response.content}


def finalize_node(state: AgentState) -> dict:
    """Package the final output."""
    return {"output": state["intermediate"]}


# ── 5. ROUTING ────────────────────────────────────────────

def should_continue(state: AgentState) -> str:
    """Decide: loop back to work, or move to finalize."""
    iteration = state.get("iteration_count", 0)
    evaluation = state.get("evaluation", "")
    decision = "finalize" if ("PASS" in evaluation or iteration >= 3) else "work"
    print(f"--- ROUTING: iteration={iteration}, decision={decision}")
    return decision


# ── 6. BUILD THE GRAPH ────────────────────────────────────

builder = StateGraph(AgentState)

# Add nodes
builder.add_node("work", work_node)
builder.add_node("evaluate", evaluate_node)
builder.add_node("finalize", finalize_node)

# Add edges
builder.add_edge(START, "work")
builder.add_edge("work", "evaluate")
builder.add_conditional_edges("evaluate", should_continue, ["work", "finalize"])
builder.add_edge("finalize", END)

# Compile
graph = builder.compile()


# ── 7. RUN IT ─────────────────────────────────────────────

if __name__ == "__main__":
    result = graph.invoke({
        "input": "Your test input here",
        "intermediate": "",
        "evaluation": "",
        "output": "",
        "iteration_count": 0
    })

    print("\n=== AGENT OUTPUT ===")
    print(result["output"])
    print(f"\n(Completed in {result['iteration_count']} iterations)")
