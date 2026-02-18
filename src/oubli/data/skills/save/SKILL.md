---
description: Save unsaved memories from the current conversation
---

# Save Memories

User-triggered memory checkpoint. Sweep the conversation and save anything Claude missed during proactive saving.

**When to run:** At the end of a session, after a long conversation, or whenever the user wants to make sure nothing was lost.

## Workflow

Execute silently (no step-by-step narration):

```
1. Review the FULL conversation from the beginning.

2. Identify memory-worthy items:
   - Preferences: likes, dislikes, style choices, tool preferences
   - Personal facts: work, family, health, location, routines
   - Decisions made: architecture choices, tool selections, approaches chosen
   - Technical patterns: workflows, conventions, project-specific knowledge
   - Opinions and corrections: strong views, "actually I prefer X", "don't do Y"
   - Behavioral signals: communication style, working style, energy patterns
   - Goals and plans: aspirations, upcoming events, project directions
   - Info about people: names, relationships, preferences of others

3. For each item, check if it was ALREADY saved during the conversation
   (call memory_search with a brief query to verify).
   Skip anything already stored.

4. For each NEW item, call memory_save() with:
   - summary: concise 1-2 sentence summary of the fact/preference/decision
   - full_text: the actual conversation excerpt where this came up
     (copy the relevant lines, not just a paraphrase)
   - topics: 1-3 topic tags (e.g., ["preferences", "food"], ["work", "tools"])
   - keywords: specific terms for search (names, tools, places)

5. Skip these — they are NOT worth saving:
   - Things already saved earlier in the conversation
   - Transient task details ("fix the bug on line 42")
   - Generic questions the user asked
   - Claude's own suggestions that the user didn't confirm
   - Temporary debugging context
```

## Output

When complete, provide a brief summary:
- Number of new memories saved
- One-line description of each (e.g., "Prefers dark mode in all editors")
- If nothing new was found: "No unsaved memories found — conversation was already well-captured."

Do NOT narrate each save — just do it and report the final result.
