# Workshop: Build Your Own Agent

> **Topic:** Multi-step agent design and implementation with LangGraph
> **Audience:** Workshop participants who completed Lectures 1-2
> **Skills practiced:** Agent architecture, LangGraph state/nodes/edges, tool integration, prompt engineering, context engineering, collaborative development
> **Estimated time:** 2.5-3 hours
> **Prerequisites:** Lectures 1 (Context Engineering) and 2 (Tooling Landscape & Agent Frameworks). Python installed. Basic Python familiarity.
> **Team size:** Pairs or groups of three

---

## Before We Start (10 minutes)

### Workshop Materials

You've been given a `workshop/` folder with everything you need. Take a moment to look through it:

| File | What It Is | When You'll Use It |
|------|------------|-------------------|
| `agent.py` | Runnable starter skeleton. A minimal working LangGraph agent you'll modify to build your own. | Phase 3 (Build It) |
| `requirements.txt` | All Python dependencies in one file. | Right now (setup) |
| `cheatsheet.md` | LangGraph quick reference: imports, state, nodes, edges, routing, debugging. Keep this open while you code. | Phases 2-4 (constantly) |
| `architecture_reference.md` | A real production LangGraph agent architecture. See how the same patterns you'll use today work at scale. | Phase 2 (Design) |
| `python_standards.md` | Python patterns reference: error handling, type hints, file organization, retry logic. | Phase 3 (Build It) |
| `test_data/emails.json` | 8 mock emails with varying urgency levels. Ready to use for an Email Triage Agent. | Phase 3 (if your agent needs email data) |
| `test_data/messy_data.csv` | 20 rows of intentionally messy data: missing values, bad formats, outliers. Ready to use for a Data Cleaning Agent. | Phase 3 (if your agent needs CSV data) |
| `test_data/article.txt` | A ~1000-word article about AI agents. Ready to use for a Research, Summarizer, or Content Agent. | Phase 3 (if your agent needs text content) |

### API Keys

You'll receive an API key at the start of the workshop. This key gives you access to the LLM that will power your agent.

Set it as an environment variable before running anything:

```bash
export OPENAI_API_KEY="sk-..."
```

Or if you're using Anthropic:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Environment Check

Install dependencies from the provided `requirements.txt`:

```bash
python --version        # 3.10+
pip install -r workshop/requirements.txt
```

Then verify the starter agent runs:

```bash
python workshop/agent.py
```

You should see output from each node (WORK NODE, EVALUATION, ROUTING) and a final result. If something is missing, raise your hand now, not in 30 minutes when your team is stuck.

### Teams

Form teams of 2-3. You'll build one agent together. One person drives (types), the others navigate (think, debug, research). Swap roles every 30 minutes or so.

---

## The Scenario

So you've spent the last two lectures understanding how modern AI actually works, how context engineering shapes the quality of everything an LLM produces, how the tooling landscape gives you different levels of control, and how LangGraph lets you build agents that can loop, branch, and make decisions. Now it's time to build one.

Here's the deal: your team is going to design, architect, and build a working multi-step agent from scratch. Not a toy example. Not a chain that runs A then B then C. An actual agent that takes in a goal, breaks it into steps, executes those steps using tools, evaluates its own output, and decides whether to keep going or stop. The kind of thing you'd actually want to use after today.

You'll choose what your agent does. You'll design its architecture. You'll write the code. And by the end of this workshop, you'll demo a working agent to the room.

The only constraint: it must be built with LangGraph, it must have at least one loop (where the agent evaluates and decides to continue or stop), and it must use at least one tool. Everything else is up to you.

---

## Phase 1: Choose Your Agent (20 minutes)

### The Idea Menu

Below is a menu of agent ideas organized by domain. Each idea includes what the agent does, what makes it interesting from an architecture perspective, and a suggested difficulty level.

**You don't have to pick from this list.** If your team has a different idea that excites you, go for it. The only requirements are: it needs a loop, it needs at least one tool, and it needs to be buildable in ~2 hours.

#### Productivity & Personal

| Agent Idea | What It Does | Why It's Interesting | Difficulty |
|---|---|---|---|
| **Email Triage Agent** | Reads a batch of emails (from `test_data/emails.json`), classifies them by urgency and type, drafts responses for the low-priority ones, and flags the important ones for human review | Multi-step classification + generation loop. The agent must decide what "important" means and handle edge cases. Mock data provided. | Medium |
| **Meeting Prep Agent** | Takes a meeting title and attendee list, researches each person (from mock profiles or web), identifies likely topics, and generates a prep brief with talking points | Research loop: gather info → evaluate completeness → gather more if needed | Medium |
| **Daily Digest Agent** | Takes a list of RSS feeds or news sources (mock or real), reads them, filters by relevance to a topic you care about, and produces a personalized summary | Filter → summarize → evaluate quality → refine loop | Easy-Medium |
| **Task Breakdown Agent** | Takes a vague goal ("Launch a podcast") and breaks it into concrete, actionable tasks with dependencies, estimates, and a suggested order | Decomposition → evaluation → refinement loop. Interesting because the agent must evaluate its own output quality | Easy-Medium |

#### Data & Research

| Agent Idea | What It Does | Why It's Interesting | Difficulty |
|---|---|---|---|
| **Research Agent** | Takes a research question, searches for information (web search or `test_data/article.txt`), evaluates whether it has enough to answer, searches more if needed, then writes a synthesis | The classic search-evaluate-loop pattern from Lecture 2. Great starting point. Mock data provided. | Easy |
| **Competitor Analysis Agent** | Takes a company name and industry, gathers data about competitors (from mock data or web), compares them on key dimensions, and produces a comparison report | Multi-source gathering + structured comparison. Interesting routing: different data sources for different competitor aspects | Medium |
| **Data Cleaning Agent** | Takes `test_data/messy_data.csv`, identifies quality issues (missing values, inconsistencies, outliers), proposes fixes, applies them, and validates the result | Clean → validate → find more issues → clean again loop. Tangible input/output. Mock data provided. | Medium |
| **Literature Review Agent** | Takes a topic, searches for relevant papers/articles (mock or real), reads abstracts, filters by relevance, and produces a structured literature review with themes | Multi-pass filtering: broad search → relevance filter → theme extraction → synthesis | Medium-Hard |

#### Communication & Content

| Agent Idea | What It Does | Why It's Interesting | Difficulty |
|---|---|---|---|
| **Blog Post Agent** | Takes a topic and target audience, outlines the post, writes a draft, critiques its own draft, and revises it | The write → critique → revise loop. Self-evaluation is the hard part | Medium |
| **Social Media Agent** | Takes a piece of long-form content (like `test_data/article.txt`) and generates platform-specific posts (Twitter thread, LinkedIn post, Instagram caption) with appropriate tone for each | Branching: different nodes for different platforms. Interesting conditional routing. Mock data provided. | Medium |
| **Translation Quality Agent** | Takes text in one language, translates it, back-translates to check accuracy, identifies issues, and re-translates problem sections | Translate → back-translate → compare → fix loop. Clear quality metric | Medium |
| **Cover Letter Agent** | Takes a job posting and a resume (or mock data), analyzes the match, identifies key points to emphasize, writes a tailored cover letter, and self-critiques for cliches and generic language | Analyze → generate → critique → revise loop with concrete quality criteria | Easy-Medium |

#### Developer Tools

| Agent Idea | What It Does | Why It's Interesting | Difficulty |
|---|---|---|---|
| **Code Review Agent** | Takes a code diff or file, reviews it for bugs, style issues, and potential improvements, categorizes findings by severity, and generates a review summary | Analysis → categorize → prioritize. Can use file I/O as a tool | Medium |
| **Documentation Agent** | Takes a code file or module, reads the code, generates documentation, checks if the documentation actually matches the code behavior, and revises | Generate → verify → revise loop. The verification step is where the architecture gets interesting | Medium |
| **Regex Builder Agent** | Takes a natural language description of a pattern and example strings, generates a regex, tests it against the examples, and iterates until all examples pass | Generate → test → evaluate → regenerate loop. Clear pass/fail criteria make the loop condition obvious | Easy-Medium |
| **API Integration Agent** | Takes an API documentation URL (or mock docs), reads the docs, generates a Python client, tests the client with sample calls, and fixes any issues | Read → generate → test → fix loop. Practical and produces a usable artifact | Hard |

### How to Choose

Pick something that:
1. **Excites your team.** You'll spend 2 hours on this. Pick something you actually want to build.
2. **Has a clear loop.** The agent should evaluate its own output and decide whether to keep going. If you can't see where the loop is, pick a different idea.
3. **Matches your confidence level.** If this is your first time writing Python with LangGraph, start with "Easy" or "Easy-Medium." The Research Agent and Task Breakdown Agent are great first agents. If your team is more experienced, go for a Medium or Medium-Hard.
4. **Produces a visible result.** At the end, you should have something you can show: a generated document, a cleaned dataset, a drafted email, a code review. Something tangible.

### What to Do in This Phase

1. Browse the menu (or pitch your own idea)
2. As a team, decide on one agent
3. Write down in one sentence: **"Our agent takes [INPUT] and produces [OUTPUT] by [PROCESS]."**
4. Raise your hand and tell the instructor what you picked (this helps us track what's happening in the room and offer targeted help)

---

## Phase 2: Design Your Architecture (25 minutes)

This is the most important phase. Teams that skip architecture and jump straight to code always end up rewriting everything an hour later. Spend the time here. It pays off.

> **Reference:** Open `architecture_reference.md` to see how a production agent system uses these same patterns at scale. Pay attention to the state machine design, the evaluate-and-fallback loop, and how tools are structured.

### Step 1: Define Your State

Everything in LangGraph revolves around state. Your state is the shared memory that every node in your graph can read from and write to. Think of it as a whiteboard that your agent updates as it works through its task.

Ask yourselves:
- What does the agent need to remember between steps?
- What's the input? What's the final output?
- What intermediate results need to be stored?
- Do you need an iteration counter (to prevent infinite loops)?

Look at the `AgentState` class in `agent.py` for a minimal example. Your state will likely need different or additional fields. Write your state definition on paper or in a file. Every field should have a reason for existing.

> **Reference:** See `cheatsheet.md` → "Define State" for the exact syntax.

### Step 2: Draw Your Graph

Before writing code, draw the graph. Seriously. On paper, on a whiteboard, in a text file. Boxes for nodes, arrows for edges, diamond shapes for decisions.

Every graph needs:
- **A START node** that kicks things off
- **At least one "work" node** that does the main task (search, generate, analyze)
- **An "evaluate" node** that looks at what the work node produced and decides: good enough, or try again?
- **A conditional edge** from the evaluate node: one path loops back, one path moves forward
- **An END node** that produces the final output

**Example graph** (Research Agent):

```
START → search → evaluate → [sufficient?]
                                ├── YES → synthesize → END
                                └── NO  → search (loop back)
```

**More complex example** (Email Triage Agent):

```
START → read_emails → classify → [for each email]
                                    ├── HIGH priority → flag_for_human
                                    └── LOW priority  → draft_response → evaluate_draft
                                                                            ├── GOOD → store_draft
                                                                            └── BAD  → draft_response (loop)
                                  → compile_report → END
```

> **Reference:** See `cheatsheet.md` → "Common Patterns" for more graph patterns (multi-source gatherer, classifier-router, self-improving generator).

### Step 3: Define Your Tools

Tools are Python functions that your agent can call to interact with the outside world. In LangGraph, you define them as regular functions decorated with `@tool`.

Think about what your agent needs to do that isn't just "think":
- Read a file? That's a tool.
- Search the web? That's a tool.
- Run a calculation? That's a tool.
- Call an external API? That's a tool.

You need at least one tool, but don't go overboard. Two or three is plenty for a workshop agent.

Look at the `example_tool` in `agent.py` for the syntax. The key thing: the docstring you write on a tool is what the LLM sees, so make it clear and specific.

**Pro tip for the workshop:** If your agent idea needs web search or email access and you don't want to deal with API setup, mock it. Create a function that returns realistic fake data. Or use the files in `test_data/` directly. The architecture and logic are what matter, not whether you're hitting a real API.

> **Reference:** See `cheatsheet.md` → "Define a Tool" for the exact decorator syntax.

### Step 4: Write It Down

Before moving to code, your team should have written down:
1. The state definition (what fields, what types)
2. The graph drawing (nodes, edges, the loop)
3. The tool list (what each tool does)
4. The loop condition (what makes the agent stop looping and move forward)

**Show this to the instructor or a neighboring team.** A second pair of eyes catches architecture problems early.

### Architecture Checklist

- [ ] State has all the fields your nodes need to read and write
- [ ] Every node has a clear single responsibility
- [ ] There is at least one loop (conditional edge that goes back)
- [ ] There is a safety valve (max iterations) to prevent infinite loops
- [ ] There is at least one tool
- [ ] You can explain the graph flow in one sentence: "The agent does X, then checks Y, and either loops back to X or moves to Z"

---

## Phase 3: Build It (60-75 minutes)

This is the longest phase. You're writing real code now.

### Getting Started

Open `agent.py`. This is your starting point: a minimal working LangGraph agent that compiles and runs. You already verified this during setup. Now you'll modify it to match your architecture.

Keep `cheatsheet.md` open in another tab or window. It has the exact syntax for everything you'll need: state definitions, tool decorators, node functions, graph building, routing, and debugging.

> **Reference:** If you want to see how a production codebase organizes its Python (error handling, type hints, file structure), glance at `python_standards.md`. You don't need to follow all of it for the workshop, but the error handling and return type patterns are useful.

### Building Guide

Work through your agent in this order:

**First 15 minutes: Get the skeleton running.**
You already ran `agent.py` during setup. Now replace the agent name, team names, and description at the top of the file. Run it again. This is your safety net: you always have a working version to fall back to.

**Next 15 minutes: Replace the state and tools.**
Swap in your real state definition and write your tools. Test the tools individually before plugging them into the graph. See `cheatsheet.md` → "Debugging" for how to test a tool in isolation.

If your agent needs test data, check the `test_data/` folder:
- `emails.json` — 8 emails with sender, subject, body, and urgency fields
- `messy_data.csv` — 20 rows with missing values, invalid ages, bad dates, non-numeric prices
- `article.txt` — a full article about AI agents, suitable for summarization or research tasks

**Next 15-20 minutes: Replace the nodes.**
Write your real node functions. Each node should do one thing. If a node is getting long (more than ~20 lines), split it into two nodes.

**Next 15-20 minutes: Wire up the graph and routing.**
Connect your nodes with edges. Write your conditional routing function. This is where the architecture drawing from Phase 2 pays off: you're just translating the drawing into code. See `cheatsheet.md` → "Build the Graph" for the exact API.

**Last 10-15 minutes: Test, debug, iterate.**
Run your agent with real input. Watch what happens at each step. The starter `agent.py` already has debug prints at every node, so you'll see the state flow. Common issues:
- The loop never stops (your routing condition is wrong, or your evaluation is never satisfied)
- The loop stops too early (your evaluation is too lenient)
- State fields are missing or the wrong type
- The LLM isn't doing what you expect (your system prompt needs work, this is context engineering from Lecture 1)

### Debugging Tips

The starter `agent.py` already prints state at every node and routing decision. If you need more visibility, add similar prints to any new nodes you write. See `cheatsheet.md` → "Debugging" for patterns on testing nodes and tools in isolation.

### When You're Stuck

1. **Re-read your architecture drawing.** Does your code match what you designed?
2. **Check the cheatsheet.** `cheatsheet.md` has the syntax for every LangGraph operation. If you're unsure about how to add a conditional edge or define a routing function, it's in there.
3. **Simplify.** If something complex isn't working, replace it with a simpler version that does work, then add complexity back.
4. **Check the state.** 90% of LangGraph bugs are state bugs: a field is missing, the wrong type, or not being updated.
5. **Ask a neighboring team.** They're building something different, but LangGraph patterns are the same.
6. **Raise your hand.** The instructor is here for exactly this.

---

## Phase 4: Validate and Polish (15-20 minutes)

### The Validation Checklist

Run through this checklist as a team. Every item should be checked before you demo.

#### Core Requirements

- [ ] The agent runs without crashing
- [ ] The agent takes a clear input and produces a clear output
- [ ] There is at least one loop (the agent evaluates and decides to continue or stop)
- [ ] The loop has a safety valve (maximum iterations) that prevents infinite loops
- [ ] There is at least one tool that the agent uses
- [ ] The output is useful and makes sense (not just "PASS" or random text)

#### Architecture Quality

- [ ] Each node has a single, clear responsibility
- [ ] State contains only what's needed (no mystery fields)
- [ ] The routing condition is based on meaningful evaluation (not just iteration count)
- [ ] The agent's system prompts are specific and well-crafted (context engineering)

#### Code Quality

- [ ] The code runs with a single command: `python agent.py`
- [ ] The one-sentence description at the top of the file is accurate
- [ ] Someone outside your team could read the code and understand what each node does

#### Bonus (if you have time)

- [ ] The agent handles edge cases gracefully (empty input, weird input)
- [ ] You added a second tool
- [ ] You added a branching path (not just a loop, but a conditional branch)
- [ ] The agent produces its output in a structured format (markdown, JSON, or saves to a file)
- [ ] You visualized your graph (see `cheatsheet.md` → "Visualize the Graph" for how)

---

## Phase 5: Demo Time (20-30 minutes)

Each team gets 2-3 minutes to show their agent to the room.

### Demo Format

1. **What does your agent do?** (One sentence. The sentence you wrote in Phase 1.)
2. **Show the graph.** (Your architecture drawing or the ASCII graph from LangGraph. Explain the loop.)
3. **Run it live.** (Give it an input. Show the output. If it loops, narrate what's happening at each step.)
4. **One thing you learned.** (What surprised you? What was harder or easier than expected? What would you do differently?)

### What Makes a Good Demo

- The agent does something real and useful
- You can explain WHY it loops (not just that it does)
- The output is visibly better because of the loop (show what iteration 1 produced vs. the final output)
- You're honest about limitations ("it doesn't handle X yet, but the architecture supports it")

---

## Reference: Common LangGraph Patterns

> These are also in `cheatsheet.md` for quick reference during coding.

### Pattern 1: The Evaluate-and-Retry Loop

The most common agent pattern. Do work, evaluate it, retry if not good enough.

```
work → evaluate → [good enough?]
                     ├── YES → finalize
                     └── NO  → work (loop)
```

### Pattern 2: The Multi-Source Gatherer

Collect information from multiple sources, then synthesize.

```
START → source_a ─┐
      → source_b ─┼── combine → evaluate → [complete?]
      → source_c ─┘                           ├── YES → synthesize → END
                                               └── NO  → [identify gaps] → source_x (loop)
```

### Pattern 3: The Classifier-Router

Classify input, then route to specialized handlers.

```
START → classify → [type?]
                     ├── TYPE_A → handler_a ──┐
                     ├── TYPE_B → handler_b ──┼── merge → END
                     └── TYPE_C → handler_c ──┘
```

### Pattern 4: The Self-Improving Generator

Generate content, critique it, improve it. Repeat until quality threshold is met.

```
generate → critique → [quality score]
                         ├── HIGH  → finalize → END
                         ├── MEDIUM → revise → critique (loop with focused fixes)
                         └── LOW   → generate (loop from scratch)
```

---

## Reference: Using the Test Data

The `test_data/` folder contains ready-to-use mock data so you can skip data generation and focus on architecture.

### `test_data/emails.json`

8 mock emails with `id`, `from`, `subject`, `body`, `urgency` (high/medium/low), and `received_at` fields. Includes a mix of urgent business emails, spam newsletters, security alerts, and team requests. Perfect for Email Triage, Daily Digest, or any classification agent.

### `test_data/messy_data.csv`

20 rows of user data with intentional quality issues: missing names, missing emails, negative ages, an age of 156, inconsistent date formats, non-numeric values in numeric fields, invalid email formats, missing signup dates, and a non-existent plan tier. Perfect for a Data Cleaning Agent.

### `test_data/article.txt`

A ~1000-word article covering the evolution from chatbots to AI agents, tool use, LangGraph/CrewAI/AutoGen frameworks, and open challenges. Perfect for Research, Blog Post, Social Media, or any content processing agent.

### Creating your own test data

If none of the provided files fit your agent idea, you can ask the LLM to generate mock data for you, or create a few hardcoded examples directly in your script. The architecture and logic are what matter, not where the data comes from.

---

## Wrap-Up

By the end of this workshop, your team has designed, architected, built, and demoed a working multi-step agent. Not a chain. Not a single LLM call with a fancy prompt. An agent that evaluates its own work and decides what to do next.

Here's what you practiced, whether you realized it or not:

- **Context engineering** (from Lecture 1): The system prompts you wrote for each node, the state you designed, the way you structured information for the LLM. That's context engineering applied to agent nodes.
- **The framework progression** (from Lecture 2): You went from understanding what LangGraph is conceptually to building a real graph with state, nodes, edges, and cycles.
- **Agent architecture**: You learned that the hard part of building agents isn't the code. It's deciding what the nodes do, what state they share, and when to loop vs. when to stop.

The agent you built today is a starting point. The architecture patterns you used (evaluate-and-retry, classifier-router, self-improving generator) are the same patterns behind production agent systems. If you want to see what that looks like, revisit `architecture_reference.md` — the production system uses the exact same patterns, just with more tools, error handling, and scale. The thinking is the same.
