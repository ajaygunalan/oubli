# Synthesize Memories

Run the full memory synthesis workflow: merge duplicates and create higher-level insights, level by level.

## Instructions

Execute this workflow silently (no narration):

```
current_level = 0

LOOP:
  1. Call memory_prepare_synthesis(level=current_level)

  2. If duplicates_merged > 0:
     - Note: "Merged {n} duplicates at Level {current_level}"

  3. If synthesis_groups == 0 or memories_remaining < 2:
     - STOP - synthesis complete

  4. For each group in groups:
     - Read all the summaries in that group
     - Create a 1-2 sentence insight that captures the pattern/theme
     - Call memory_synthesize(
         parent_ids=[list of IDs from group],
         summary="your insight",
         topics=[the topic],
         delete_parents=false
       )

  5. current_level += 1
  6. GOTO LOOP
```

## Output

When complete, provide a brief summary:
- Levels processed
- Total duplicates merged
- Syntheses created

Do NOT narrate each step - just do it and report the final result.
