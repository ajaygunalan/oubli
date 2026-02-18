# Plan: Migrate Oubli commands to skills

## Context

Oubli's 4 slash commands (`clear-memories`, `save`, `synthesize`, `visualize-memory`) live in `.claude/commands/` as flat `.md` files. The user wants them as proper skills (`.claude/skills/<name>/SKILL.md`) to align with Claude Code's newer skill format and enable future integration with Vegapunk skills in robo_thesis.

## Changes

### 1. Create source skill directories

Replace `src/oubli/data/commands/` with `src/oubli/data/skills/`:

```
src/oubli/data/skills/
├── clear-memories/SKILL.md
├── save/SKILL.md
├── synthesize/SKILL.md
└── visualize-memory/SKILL.md
```

Each gets proper YAML frontmatter. Body content stays the same.

Frontmatter per skill:
- **clear-memories**: `description`, `allowed-tools: Bash`, `disable-model-invocation: true` (destructive — user-only)
- **save**: `description` (user and agent invocable)
- **synthesize**: `description` (user and agent invocable)
- **visualize-memory**: `description`, `allowed-tools: Bash` (user and agent invocable)

### 2. Update `src/oubli/cli.py`

**setup() docstring** (line 90): Change `.claude/commands/ (slash commands)` to `.claude/skills/`.

**setup() install logic** (lines 141-152): Iterate `src/oubli/data/skills/` subdirs, `shutil.copytree` each into `.claude/skills/<name>/`. Also delete old `.claude/commands/{clear-memories,save,synthesize,visualize-memory}.md` if present (backward compat cleanup).

**uninstall()** (lines 334-343): Remove skill dirs from `.claude/skills/` AND old command files from `.claude/commands/` (covers both old and new installs). Add `save` to the list.

**Summary output** (line 189): Update to say "Skills" and list all 4 including `/save`.

**Echo messages**: Change "Installing slash commands..." to "Installing skills..." etc.

### 3. Update docs

- `CLAUDE.md` (root): Rename "Slash Commands" section to "Skills", update package structure tree to show `skills/` subdirs
- `src/oubli/data/CLAUDE.md` — already skill-agnostic (line 154 says "user-triggered via /synthesize"). No change needed.

### 4. Delete old source directory

Remove `src/oubli/data/commands/` entirely.

### 5. Install and verify

1. `pipx install --force /home/ajay/agent-memory/oubli/`
2. `cd /media/ajay/gdrive/_robo_thesis/ && oubli setup`
3. Verify `.claude/skills/{clear-memories,save,synthesize,visualize-memory}/SKILL.md` exist
4. Verify old `.claude/commands/{clear-memories,save,synthesize,visualize-memory}.md` are cleaned up
5. Verify no conflicts with existing vp-* and obsidian-* skills

### 6. Commit and push

Single commit to `origin/main`.

## Files to modify

- `src/oubli/data/skills/clear-memories/SKILL.md` (new)
- `src/oubli/data/skills/save/SKILL.md` (new)
- `src/oubli/data/skills/synthesize/SKILL.md` (new)
- `src/oubli/data/skills/visualize-memory/SKILL.md` (new)
- `src/oubli/data/commands/` (delete entire directory)
- `src/oubli/cli.py` (setup, uninstall, summary output)
- `CLAUDE.md` (root — rename "Slash Commands" to "Skills", update package structure tree)
