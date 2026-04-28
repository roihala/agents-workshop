"""
Agent: [YOUR AGENT NAME]
Team: [YOUR NAMES]
Description: [ONE SENTENCE]

Provider: Anthropic Claude (via langchain-anthropic)
Model:    claude-haiku-4-5-20251001 — fast, cheap, ideal for workshop use

Setup
-----
1. Install dependencies:
       pip install -r requirements.txt
2. Export your Anthropic API key (get one at https://console.anthropic.com/settings/keys):
       export ANTHROPIC_API_KEY=sk-ant-...
3. Run:
       python agent.py

Architecture
------------
LangGraph state machine with three nodes:
    work → evaluate → (loop back to work, or finalize)

The evaluator returns PASS/FAIL; the router loops back to `work` on FAIL,
up to `iteration_count >= 1` (capped low to keep API usage modest in class).
Bump that cap in `should_continue` once your own quota allows it.

Swapping the model provider
---------------------------
Everything provider-specific lives in the MODEL section below. To switch to
OpenAI or Google, replace the import and constructor there — the rest of the
graph is provider-agnostic (it only uses `langchain_core` message types).
"""

from typing import TypedDict
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
# To switch providers, replace the import + constructor below.
# Examples:
#   OpenAI:  from langchain_openai import ChatOpenAI
#            llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.environ["OPENAI_API_KEY"], ...)
#   Google:  from langchain_google_genai import ChatGoogleGenerativeAI
#            llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.environ["GEMINI_API_KEY"], ...)
#
# `max_retries=5` lets the LangChain wrapper transparently absorb rate-limit
# 429s with exponential backoff — useful when many students share one key.
# NEVER hardcode the API key here — always read from an environment variable
# so the file stays safe to commit.

import os
from langchain_anthropic import ChatAnthropic

llm = ChatAnthropic(
    model="claude-haiku-4-5-20251001",
    temperature=0,
    api_key=os.environ["ANTHROPIC_API_KEY"],
    max_retries=5,
)


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
    decision = "finalize" if ("PASS" in evaluation or iteration >= 1) else "work"
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
