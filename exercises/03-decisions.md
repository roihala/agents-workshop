# Exercise 3: Start Your DECISIONS.md

> This file lives with you throughout the workshop. Every time you make a choice, write it down. By the end, you'll have a record of WHY your agent looks the way it does.

## What is DECISIONS.md?

A decisions log documents the choices you make while implementing. Not what you built, but **why you built it that way**, and what alternatives you considered.

Code tells you WHAT. Commits tell you WHEN. The decisions file tells you WHY.

Six months from now, when someone (or future-you) asks "why did you use two separate nodes here instead of one?", the answer is in this file.

## Instructions

Create a file called `DECISIONS.md` in your project root. Start it with this structure:

```markdown
# Decisions Log

> Architecture and implementation decisions for [Your Agent Name].
> Updated as we build.

## Format

Each entry follows this pattern:

### [Short title of the decision]
- **Date:** [today]
- **Status:** decided | revisited | reversed
- **Context:** What situation prompted this decision?
- **Decision:** What did you choose?
- **Alternatives:** What else did you consider?
- **Why:** Why this option over the others?
```

### Seed it with your first decisions

You've already made decisions during Exercise 1 and 2. Go back and capture them. You should have at least 2-3 entries already. Examples of decisions you've likely made:

- **Which agent idea to build** — Why this one? What other ideas did you consider?
- **State design** — Why these fields? Did you add or remove any while planning?
- **Loop strategy** — What does "good enough" mean for your agent? Why that threshold?
- **Tool choices** — Why these tools? What alternatives exist?

### Keep it open while you code

As you implement, you'll hit decision points:
- "Should I split this into two nodes or keep it as one?"
- "Should the evaluator check for X or Y?"
- "The model keeps returning Z — should I change the prompt or add a retry?"

When that happens, add an entry. It takes 30 seconds and saves hours of confusion later.

## What makes a good entry

**Good:** "We split the processing into classify and draft nodes because a single node was producing inconsistent output — it would sometimes skip classification and go straight to drafting."

**Bad:** "We used two nodes." (This tells you nothing about why.)

**Good:** "We set max iterations to 3 because testing showed the output quality plateaued after 2 iterations, and a 4th iteration hit rate limits."

**Bad:** "Max iterations is 3." (No reasoning, no context.)

## Quality check

Before you start coding:
- [ ] Does the file exist with the format template?
- [ ] Are there at least 2 entries from your planning phase?
- [ ] Does each entry include context, decision, and reasoning?

## Time

~5 minutes to set up. Then ongoing throughout the workshop. Keep it open in a tab.
