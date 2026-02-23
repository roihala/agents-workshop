# Exercise 2: Write Your ARCHITECTURE.md

> Now that you know WHAT you're building, plan HOW it works. This is where you design the internals before touching code.

## What is ARCHITECTURE.md?

An architecture document describes the technical structure of your system. For an agent, that means: what are the moving parts, how do they connect, and how does data flow through the system.

This is the document you'd draw on a whiteboard if someone asked "walk me through how this thing works under the hood."

## Instructions

Create a file called `ARCHITECTURE.md` in your project root. It should include:

### 1. State definition
What does your agent need to remember as it works? List every field in your state and explain what it holds.

Example:
```
| Field           | Type   | Purpose                              |
|-----------------|--------|--------------------------------------|
| input           | str    | Raw user input                       |
| classified      | str    | Category assigned by classifier node |
| draft           | str    | Current working output               |
| evaluation      | str    | Pass/fail judgment from evaluator    |
| iteration_count | int    | Safety counter for the loop          |
```

Be deliberate about state. Every field should earn its place. If you can't explain why a field exists, remove it.

### 2. Nodes
List each node (processing step) in your graph. For each one, describe:
- **What it does** (one sentence)
- **What state it reads**
- **What state it writes**

Example:
```
### classify_node
- Reads: input
- Writes: classified
- Classifies the input into one of: [urgent, informational, spam]
```

### 3. Edges and routing
Draw your graph. ASCII art is fine. Show:
- The flow from START to END
- Where conditional routing happens
- Where loops exist

Example:
```
START → classify → route → [urgent?]
                              ├── YES → draft_urgent → evaluate → [pass?]
                              │                                      ├── YES → finalize → END
                              │                                      └── NO  → draft_urgent (loop)
                              └── NO  → draft_standard → END
```

### 4. Tools
List each tool your agent uses. For each one:
- **Name**
- **What it does**
- **When the agent calls it**

If your agent doesn't use any tools yet, list the tools you plan to add and why.

### 5. The loop
Every agent in this workshop must have at least one loop. Describe:
- What triggers a retry?
- What does "good enough" look like?
- What's the safety valve? (max iterations)

## Quality check

Before moving on:
- [ ] Could a teammate read this and implement the agent without asking you questions?
- [ ] Does the state have only the fields it needs?
- [ ] Is the graph drawn out with clear edges?
- [ ] Is the loop exit condition defined?
- [ ] Are the tools listed with clear purposes?

## Time

~15 minutes. Spend the time here. A solid architecture saves you debugging time later.
