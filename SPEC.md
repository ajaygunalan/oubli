# Oubli: Fractal Memory System for Claude Code

> *"oubli"* (French for "forgetting") — Ironically, a system that never forgets.

## Overview

Oubli is a Claude Code plugin that provides persistent, hierarchical memory with fractal synthesis. It mimics human memory consolidation: raw experiences are stored, then progressively abstracted into higher-level insights over time.

**Goal:** Create a viral, easy-to-install GitHub project that gives Claude Code the persistent memory it deserves.

---

## Core Concept: Fractal Memory

### Memory Levels

```
           ┌─────────────────────────────────────────┐
           │            CORE MEMORY                  │
           │    (~2K tokens, always in context)      │
           │                                         │
           │  The essential "you" - personality,     │
           │  key preferences, life context, work    │
           └─────────────────────┬───────────────────┘
                                 │ (distilled from)
                                 ▼
Level 2+   ○ "Max deeply appreciates jazz guitar, especially fusion"
(insights)  ╱╲
           ╱  ╲
Level 1   ○    ○  "Loves Pat Metheny"  "Studies jazz voicings"
(themes)  │╲  ╱│
          │ ╲╱ │
Level 0   ○ ○ ○ ○  Raw conversation chunks with full text
(raw)
```

- **Core Memory:** A ~2K token distillation of the most important facts about the user. Always loaded. Updated periodically.
- **Level 0 (raw):** Complete conversation chunks with full text, summary, metadata
- **Level 1+ (synthesized):** Abstracted insights derived from clustering lower-level memories
- Memories link to their parents (what they were synthesized from) and children (what they synthesized into)

### Core Memory

The Core Memory is a special, always-present context block (~2K tokens) that contains the most essential information about the user. Unlike regular memories that are retrieved on-demand, Core Memory is injected into every conversation.

**Contents:**
- Identity: Name, location, key relationships
- Work: Role, company, primary skills, current projects
- Personality: Communication preferences, values, working style
- Key preferences: Technical choices, tools, patterns
- Current focus: What's top-of-mind right now

**Storage:** `~/.oubli/core_memory.md` - A markdown file that can be viewed/edited directly.

**Update triggers:**
1. **After synthesis:** When Level 1+ memories are created, evaluate if they should update Core Memory
2. **Manual:** User can run `/oubli:core update` to regenerate
3. **Periodic:** After N new memories, re-evaluate Core Memory
4. **On import:** After importing Claude.ai memory, generate initial Core Memory

**Update process:**
1. Load current Core Memory
2. Load all Level 1+ memories (summaries only)
3. LLM prompt: "Given these insights about the user, update the Core Memory to reflect the most important, stable facts. Keep to ~2K tokens. Prioritize: identity, work context, personality, key preferences, current focus."
4. Save updated Core Memory

**Key principle:** Core Memory should be **stable**. It changes slowly. Transient interests or one-off topics don't belong here. It's the "essence" of the user that's valuable in every conversation.

### Key Principle

Both storage AND retrieval are fractal:
- **Storage:** Raw → synthesized when thresholds are met AND synthesis makes semantic sense
- **Retrieval:** Search summaries first → drill down to full text only when needed

---

## Architecture

### Tech Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Storage | LanceDB | Embedded (no server), hybrid search built-in, just files |
| Embeddings | sentence-transformers | Local, no API key, `all-MiniLM-L6-v2` (~80MB) |
| Interface | Claude Code Plugin | Hooks + MCP server + subagents + commands |
| Language | Python | Ecosystem, ease of install |

### Directory Structure

```
oubli/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── commands/
│   ├── memory.md                # /oubli:memory search|stats|export
│   ├── recall.md                # /oubli:recall "query"
│   ├── synthesize.md            # /oubli:synthesize [--scope X]
│   ├── import.md                # /oubli:import (bootstrap from text)
│   └── core.md                  # /oubli:core view|update|edit
├── agents/
│   └── synthesizer.md           # Subagent for memory consolidation
├── skills/
│   └── memory-awareness/
│       └── SKILL.md             # Auto-invoked for context retrieval
├── hooks/
│   └── hooks.json               # SessionStart, Stop hooks
├── src/
│   ├── __init__.py
│   ├── cli.py                   # CLI commands: init, import, search, stats
│   ├── mcp_server.py            # MCP tools for Claude Code
│   ├── storage.py               # LanceDB interface
│   ├── embeddings.py            # Local embedding model wrapper
│   ├── synthesis.py             # Fractal synthesis logic
│   ├── core_memory.py           # Core Memory management
│   └── import_parser.py         # Chunking + metadata extraction
├── pyproject.toml               # Package definition
└── README.md
```

**User data directory (`~/.oubli/`):**
```
~/.oubli/
├── config.toml                  # User configuration
├── core_memory.md               # Core Memory (~2K tokens, always loaded)
├── memories.lance/              # LanceDB database
└── models/                      # Cached embedding models
```

---

## Data Model

### Memory Schema

```python
@dataclass
class Memory:
    id: str                         # UUID
    level: int                      # 0 = raw, 1+ = synthesized
    
    # Content
    summary: str                    # Always present, used for search (~200 tokens max)
    full_text: str | None           # Only for level 0, stores complete conversation
    
    # Hierarchy
    parent_ids: list[str]           # Memories this was synthesized from
    child_ids: list[str]            # Raw memories that led to this
    
    # Metadata
    topics: list[str]               # e.g., ["work", "coding", "python"]
    keywords: list[str]             # Extracted keywords for search
    source: str                     # "conversation", "import", "manual"
    
    # Embeddings
    embedding: list[float]          # Vector for semantic search
    
    # Timestamps & access
    created_at: datetime
    updated_at: datetime
    last_accessed: datetime
    access_count: int
    
    # Synthesis tracking
    synthesis_attempts: int         # Prevents infinite retry on non-synthesizable clusters
    confidence: float               # How confident the synthesis is (0-1)
```

---

## Plugin Components

### 1. Hooks (hooks/hooks.json)

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "oubli session-start"
      }]
    }],
    "Stop": [{
      "hooks": [{
        "type": "prompt",
        "prompt": "Review this conversation and decide if a memory should be saved.\n\nCriteria for saving:\n- New factual information about the user\n- Decisions or preferences expressed\n- Project context worth preserving\n- Insights or learnings\n- Corrections to previous assumptions\n\nIf saving, call memory_save with:\n- summary: Concise summary (1-3 sentences)\n- full_text: Complete conversation since last memory save\n- topics: Relevant topic categories\n- keywords: Searchable keywords\n\nAlso consider: Should Core Memory be updated? If this conversation revealed something fundamental about the user (identity, core preferences, major life/work changes), call core_memory_update after saving.\n\nIf not saving, respond: {\"save\": false, \"reason\": \"...\"}\n\nConversation context: $ARGUMENTS"
      }]
    }]
  }
}
```

**SessionStart:** 
1. Loads Core Memory (~2K tokens, always)
2. Optionally loads relevant memories based on working directory, recent topics

**Stop:** 
1. LLM-based decision on whether to save a memory
2. Also evaluates if Core Memory needs updating

### 1b. Core Memory Structure

The Core Memory is stored as `~/.oubli/core_memory.md` with a structured format:

```markdown
# Core Memory
> Last updated: 2025-01-11T14:30:00Z
> Version: 7

## Identity
- Name: Max Leander
- Location: Sweden
- Born: October 31, 1984
- Partner: Katherine (from Philippines, lived in Sweden since 2008)
- Children: Karla (2012), David (2019), Elysia (2025)

## Work
- Role: Senior Data Scientist & ML/AI Engineering Consultant
- Company: Data Wealth AB (own company)
- Current client: Choreograph (building LLM-based research agents)
- Background: Spotify (2022-2023), King, HelloFresh, PriceSpy
- Primary skills: Python, A/B testing, RAG systems, LLM applications

## Personality & Working Style
- Communication: Direct, prefers actionable responses
- Goal: Minimize procrastination - wants concrete next steps
- Learning: Currently pursuing ML/AI research curriculum (12 weeks)
- Values efficiency and specific version numbers in dependencies

## Key Preferences
- Languages: Python primary, bilingual Swedish/English
- When recommending packages: Always include specific versions
- Coding style: Step-by-step solutions with concrete implementations
- Fitness: Strength training 2-5x/week, 1900 cal/day target

## Current Focus
- 12-week ML/AI research curriculum (transformers, deep learning)
- Consulting opportunities (recent Spotify contractor applications)
- Building RAG chatbots and LLM-based agents
- This project: Oubli - fractal memory system for Claude Code
```

**Sections are fixed** but content within them evolves. This structure ensures:
- Easy parsing for updates
- Human-readable and editable
- Versioned for tracking changes
- Timestamp for staleness detection

### Core Memory Update Process

```python
def update_core_memory(focus_areas: list[str] = None):
    # 1. Load current Core Memory
    current = load_core_memory()
    
    # 2. Load all Level 1+ memory summaries
    insights = get_memories_by_level(min_level=1, limit=100)
    
    # 3. Load recent Level 0 memories (last 20)
    recent = get_recent_memories(limit=20, level=0)
    
    # 4. Construct update prompt
    prompt = f"""
    Current Core Memory:
    {current}
    
    High-level insights from memory:
    {format_memories(insights)}
    
    Recent conversations:
    {format_memories(recent)}
    
    Task: Update the Core Memory to reflect the most important, stable facts about this user.
    
    Rules:
    - Keep total length ~2000 tokens
    - Preserve the section structure (Identity, Work, Personality, Preferences, Focus)
    - Only include information that's valuable in EVERY conversation
    - Prioritize stable facts over transient interests
    - "Current Focus" can change more frequently than other sections
    - If focus_areas specified, pay special attention to: {focus_areas}
    - Increment the version number
    - Update the timestamp
    
    Output the complete updated Core Memory in markdown format.
    """
    
    # 5. Generate updated Core Memory (via Claude)
    updated = generate_with_llm(prompt)
    
    # 6. Save
    save_core_memory(updated)
    
    return updated
```

**Update is conservative:** Core Memory should change slowly. Most conversations don't warrant an update. The Stop hook evaluates this.

### 2. MCP Server Tools

```python
tools = [
    {
        "name": "memory_search",
        "description": "Search memories by semantic similarity and keywords. Returns summaries only.",
        "parameters": {
            "query": "string - Search query",
            "limit": "int (default 5) - Max results",
            "min_level": "int (default 0) - Minimum abstraction level",
            "topics": "list[string] (optional) - Filter by topics"
        }
    },
    {
        "name": "memory_get_detail",
        "description": "Get full text for specific memory IDs. Use after memory_search when more detail is needed.",
        "parameters": {
            "ids": "list[string] - Memory IDs to retrieve"
        }
    },
    {
        "name": "memory_save",
        "description": "Save a new memory from the current conversation.",
        "parameters": {
            "summary": "string - Concise summary",
            "full_text": "string - Complete text to store",
            "topics": "list[string] - Topic categories",
            "keywords": "list[string] - Searchable keywords"
        }
    },
    {
        "name": "memory_import",
        "description": "Import memories from a text block (e.g., Claude.ai memory export).",
        "parameters": {
            "text": "string - Text to import",
            "format": "string (optional) - auto|claude-ai|markdown|json",
            "source": "string (optional) - Source label for imported memories"
        }
    },
    {
        "name": "memory_synthesize",
        "description": "Trigger memory consolidation. Clusters similar memories and creates higher-level insights.",
        "parameters": {
            "scope": "string (optional) - all|topic:X|level:N (default: all)",
            "dry_run": "bool (optional) - Preview without saving"
        }
    },
    {
        "name": "memory_stats",
        "description": "Get memory system statistics.",
        "parameters": {}
    },
    {
        "name": "core_memory_get",
        "description": "Get the current Core Memory content. This is automatically loaded at session start, but can be explicitly retrieved.",
        "parameters": {}
    },
    {
        "name": "core_memory_update",
        "description": "Regenerate Core Memory from current insights. Use after significant new information or synthesis.",
        "parameters": {
            "focus_areas": "list[string] (optional) - Areas to prioritize in update (e.g., ['work', 'current_projects'])"
        }
    },
    {
        "name": "core_memory_edit",
        "description": "Directly edit a section of Core Memory. Use for corrections or adding specific important facts.",
        "parameters": {
            "section": "string - Section to edit (identity|work|preferences|personality|focus)",
            "content": "string - New content for the section"
        }
    }
]
```

### 3. Synthesizer Subagent (agents/synthesizer.md)

```markdown
---
name: oubli-synthesizer
description: Consolidates memories into higher-level insights
allowedTools:
  - memory_search
  - memory_get_detail
  - memory_save
---

# Memory Synthesizer

You consolidate clusters of related memories into higher-level insights.

## Input

You receive a cluster of memory summaries at level N, grouped by embedding similarity.

## Process

1. Analyze the semantic coherence of the cluster
2. Determine if synthesis would create a more useful abstraction
3. Return a decision with rationale

## Decision Types

### SYNTHESIZE
Use when:
- Memories share a clear theme that can be meaningfully abstracted
- Combining creates more useful insight than individuals
- No critical nuance would be lost

Output:
```json
{
  "decision": "synthesize",
  "summary": "The synthesized insight (1-3 sentences)",
  "topics": ["topic1", "topic2"],
  "keywords": ["keyword1", "keyword2"],
  "confidence": 0.85,
  "reason": "Brief explanation"
}
```

### KEEP_SEPARATE
Use when:
- Memories are topically related but contain distinct valuable specifics
- Synthesis would lose important nuance
- Different conclusions or contexts that shouldn't merge

Output:
```json
{
  "decision": "keep_separate",
  "reason": "Brief explanation"
}
```

### DEFER
Use when:
- Cluster has too few memories (below threshold)
- Memories are too recent and may gain context later

Output:
```json
{
  "decision": "defer",
  "reason": "Brief explanation"
}
```

## Examples

**Good synthesis:**
- 5 memories about specific jazz guitarists → "User has deep appreciation for jazz guitar, especially fusion players with complex harmonic sensibilities"

**Keep separate:**
- Preferences for Python vs Rust vs Go → Should remain distinct, each has specific context

**Defer:**
- Only 2 memories about a topic that just came up
```

### 4. Memory Awareness Skill (skills/memory-awareness/SKILL.md)

```markdown
# Memory Awareness

This skill enables automatic memory retrieval based on conversation context.

## When to Activate

- User references past conversations or shared knowledge
- User asks about their preferences, projects, or history
- Context would benefit from personalization
- User explicitly asks what you remember

## Behavior

1. Use memory_search with relevant query terms
2. If results are promising but need detail, use memory_get_detail
3. Incorporate relevant memories naturally into response
4. Never fabricate memories - only use what's retrieved

## Integration

Memories should inform responses naturally, not be explicitly quoted unless the user asks what you remember about them.
```

---

## Synthesis Algorithm

### Trigger Conditions

Synthesis runs when:
1. **Manual:** User runs `/oubli:synthesize`
2. **Threshold:** Level N has more than `SYNTHESIS_THRESHOLD` memories (default: 10)
3. **Scheduled:** (Future) Background job

### Process

```python
def synthesize(scope: str = "all", dry_run: bool = False):
    # 1. Get memories at target level
    memories = get_memories_by_level(level=0)  # Start with raw
    
    # 2. Cluster by embedding similarity
    clusters = cluster_by_embedding(memories, min_cluster_size=3)
    
    # 3. For each cluster, invoke synthesizer subagent
    for cluster in clusters:
        # Skip if cluster was recently attempted and failed
        if all(m.synthesis_attempts > 2 for m in cluster):
            continue
            
        decision = invoke_synthesizer_agent(cluster)
        
        if decision.type == "synthesize":
            # Create new level-1 memory
            new_memory = Memory(
                level=1,
                summary=decision.summary,
                full_text=None,
                parent_ids=[m.id for m in cluster],
                topics=decision.topics,
                keywords=decision.keywords,
                confidence=decision.confidence
            )
            
            if not dry_run:
                save_memory(new_memory)
                # Update children to point to new parent
                for m in cluster:
                    m.child_ids.append(new_memory.id)
                    update_memory(m)
        
        elif decision.type == "keep_separate":
            # Mark memories as attempted
            for m in cluster:
                m.synthesis_attempts += 1
                update_memory(m)
        
        # DEFER: do nothing, will retry later
    
    # 4. Recursively synthesize higher levels if thresholds met
    level_1_count = count_memories_at_level(1)
    if level_1_count >= SYNTHESIS_THRESHOLD:
        synthesize_level(level=1)  # Level 1 → Level 2
```

### Fractal Property

The same algorithm applies recursively:
- Level 0 → Level 1 (raw → themes)
- Level 1 → Level 2 (themes → broader insights)
- Level 2 → Level 3 (insights → fundamental understanding)
- And so on...

Each level has its own threshold. Higher levels require more children before synthesis is attempted.

---

## Import System

### Purpose

Bootstrap the memory database from existing context (e.g., Claude.ai memory export).

### Command

```bash
# Within Claude Code
/oubli:import

# Or via CLI
oubli import --from-clipboard
oubli import memory-export.md
cat memory.txt | oubli import -
```

### Supported Formats

1. **Claude.ai memory export** - Structured with `**Headers**` and `*Subheaders*`
2. **Markdown with headers** - Split on `#`, `##`, etc.
3. **Plain text** - Paragraph-based chunking
4. **JSON** - Structured array of memories

### Import Flow

```
Input Text
    │
    ▼
Detect Format (auto or specified)
    │
    ▼
Chunk into segments (format-specific parser)
    │
    ▼
For each chunk:
    ├─ Extract metadata via LLM (when running in Claude Code)
    │  OR
    └─ Extract metadata via heuristics (CLI fallback)
    │
    ▼
Generate embeddings (batch)
    │
    ▼
Store as level-0 memories
    │
    ▼
Output summary (count by topic)
```

### Claude.ai Format Parser

```python
def parse_claude_ai_memory(text: str) -> list[Chunk]:
    """
    Parses Claude.ai memory export format:
    
    **Work context**
    Content here...
    
    **Personal context**
    Content here...
    
    *Recent months*
    Subcontent...
    """
    chunks = []
    
    # Split by **Bold Headers**
    sections = re.split(r'\*\*([^*]+)\*\*', text)
    
    current_topic = None
    for i, section in enumerate(sections):
        if i % 2 == 1:  # Header
            current_topic = normalize_topic(section)
        else:
            content = section.strip()
            if not content:
                continue
            
            # Check for *Italic Subheaders*
            subsections = re.split(r'\*([^*]+)\*', content)
            
            if len(subsections) > 1:
                current_subtopic = None
                for j, sub in enumerate(subsections):
                    if j % 2 == 1:
                        current_subtopic = normalize_topic(sub)
                    else:
                        if sub.strip():
                            chunks.append(Chunk(
                                text=sub.strip(),
                                topic=current_topic,
                                subtopic=current_subtopic,
                                source="claude_ai_import"
                            ))
            else:
                # No subsections - chunk by paragraph
                for para in content.split('\n\n'):
                    if para.strip():
                        chunks.append(Chunk(
                            text=para.strip(),
                            topic=current_topic,
                            source="claude_ai_import"
                        ))
    
    return chunks
```

### LLM-Based Metadata Extraction (within Claude Code)

When import runs within Claude Code, use a prompt to extract rich metadata:

```
For this text chunk, extract:
1. summary: A 1-2 sentence summary
2. topics: List of topic categories (e.g., work, personal, coding, preferences)
3. keywords: 5-10 searchable keywords
4. entities: Named entities (people, projects, tools, places)

Text:
{chunk_text}

Respond in JSON format.
```

### Heuristic Fallback (CLI without LLM)

```python
def extract_metadata_heuristic(text: str) -> Metadata:
    # Keywords via RAKE or simple TF-IDF
    keywords = extract_keywords_rake(text)[:10]
    
    # Topics via keyword matching
    topics = detect_topics_by_keywords(text)
    
    # Summary = first sentence
    summary = text.split('.')[0][:200]
    
    return Metadata(summary=summary, topics=topics, keywords=keywords)
```

---

## Installation Experience

### Target UX

```bash
# One command
pip install oubli

# Initialize (run within Claude Code for best experience)
# This will:
# 1. Set up ~/.oubli/ directory
# 2. Download embedding model (~80MB, one-time)
# 3. Configure Claude Code plugin
# 4. Optionally import existing Claude.ai memory
/oubli:init

# That's it. Start using Claude Code normally.
```

### Init Flow (within Claude Code)

```
/oubli:init
    │
    ▼
Check if ~/.oubli exists
    │
    ├─ Yes → "Oubli already initialized. Run /oubli:stats"
    │
    └─ No ─┐
           ▼
    Create ~/.oubli/
    Download embedding model (with progress)
           │
           ▼
    "Would you like to import existing memory?"
           │
    ├─ Yes → "Paste your Claude.ai memory export, or provide a file path"
    │        → Parse and import
    │        → Generate initial Core Memory from imported data
    │        → Show summary
    │
    └─ No → "Let's create your Core Memory. Tell me about yourself:"
           → Interactive conversation to gather key facts
           → Generate initial Core Memory
           │
           ▼
    "✓ Oubli initialized. Memory system active."
    "Your Core Memory (~2K tokens) will be loaded in every conversation."
    "Tip: Run /oubli:core view to see it, /oubli:core edit to modify."
```

### CLI Init (fallback)

```bash
oubli init
# Creates directories, downloads model
# Does not configure Claude Code plugin (manual step)

oubli import memory.md
# Import without LLM assistance (heuristic metadata)
```

---

## Retrieval Flow

### On Session Start

```
New session begins
        │
        ▼
SessionStart hook triggered
        │
        ▼
┌───────────────────────────────────────┐
│ 1. Load Core Memory (ALWAYS)          │
│    ~/.oubli/core_memory.md            │
│    ~2K tokens of essential context    │
└───────────────────────┬───────────────┘
                        │
                        ▼
┌───────────────────────────────────────┐
│ 2. Context-aware memory search        │
│    - Detect working directory/project │
│    - Load project-relevant memories   │
│    - ~1-2K additional tokens          │
└───────────────────────┬───────────────┘
                        │
                        ▼
        Agent now has ~3-4K tokens of context
        (Core Memory + relevant memories)
```

### On User Prompt

```
User prompt arrives
        │
        ▼
Core Memory already in context (from SessionStart)
        │
        ▼
┌───────────────────────────────────────┐
│ Memory search (if relevant)           │
│ - Extract likely topics from prompt   │
│ - Search memories (summaries only)    │
│ - Return top-k relevant summaries     │
│ - ~1-2K additional tokens             │
└───────────────────────┬───────────────┘
                        │
                        ▼
Agent decides: need more detail?
                        │
        ┌───────────────┴───────────────┐
        │ Yes                           │ No
        ▼                               │
memory_get_detail(ids)                  │
Fetch full_text for specific memories   │
        │                               │
        └───────────────┬───────────────┘
                        │
                        ▼
            Respond with context
```

### Context Budget

| Source | Tokens | When Loaded |
|--------|--------|-------------|
| Core Memory | ~2,000 | Always (SessionStart) |
| Project memories | ~1,000 | SessionStart if in project dir |
| Query-relevant memories | ~1,000 | On-demand during conversation |
| Full text retrieval | Variable | On-demand when detail needed |
| **Total baseline** | **~3-4K** | Every conversation |

### Hybrid Search Implementation

```python
def search_memories(query: str, limit: int = 5, min_level: int = 0) -> list[Memory]:
    # 1. Generate query embedding
    query_embedding = embed(query)
    
    # 2. LanceDB hybrid search (BM25 + vector)
    results = lance_table.search(
        query_embedding,
        query_type="hybrid"  # Combines keyword + semantic
    ).where(f"level >= {min_level}").limit(limit * 2)  # Over-fetch for reranking
    
    # 3. Boost by recency and access count
    scored = []
    for r in results:
        recency_score = compute_recency_score(r.created_at)
        access_score = log(r.access_count + 1)
        final_score = r._distance * 0.7 + recency_score * 0.2 + access_score * 0.1
        scored.append((r, final_score))
    
    # 4. Sort and return top-k
    scored.sort(key=lambda x: x[1], reverse=True)
    return [m for m, _ in scored[:limit]]
```

---

## Configuration

### Config File (~/.oubli/config.toml)

```toml
[storage]
path = "~/.oubli/memories.lance"

[embeddings]
model = "all-MiniLM-L6-v2"  # or "bge-base-en-v1.5" for higher quality

[core_memory]
path = "~/.oubli/core_memory.md"
max_tokens = 2000
auto_update_threshold = 20  # Update Core Memory after N new memories
sections = ["identity", "work", "personality", "preferences", "focus"]

[synthesis]
threshold_level_0 = 10  # Min memories before attempting synthesis
threshold_level_1 = 7
threshold_level_2 = 5
min_cluster_size = 3
max_synthesis_attempts = 3

[retrieval]
default_limit = 5
context_budget_tokens = 4000  # Excluding Core Memory

[hooks]
auto_save = true  # Use Stop hook to auto-save memories
auto_load = true  # Use SessionStart hook to load context
```

---

## MVP Scope

### v0.1.0 (Launch)

- [x] `pip install oubli` with zero external dependencies beyond Python
- [x] LanceDB storage with hybrid search
- [x] Local embeddings (sentence-transformers, no API key)
- [x] MCP server with 6 tools (search, get_detail, save, import, synthesize, stats)
- [x] Claude Code plugin with hooks (SessionStart, Stop)
- [x] Synthesizer subagent
- [x] Import from Claude.ai format
- [x] CLI for manual operations (init, import, search, stats)
- [x] Memory awareness skill
- [x] Good README with demo GIF

### v0.2.0

- [ ] Web UI for browsing memories
- [ ] Memory graph visualization
- [ ] Export to markdown
- [ ] Scheduled synthesis (background)
- [ ] Multi-workspace support

### v0.3.0

- [ ] Git-based sync between machines
- [ ] Import from ChatGPT, Gemini
- [ ] Custom embedding models
- [ ] Memory sharing (export/import between users)

---

## File-by-File Implementation Order

1. **`pyproject.toml`** - Package definition, dependencies
2. **`src/storage.py`** - LanceDB schema, CRUD operations
3. **`src/embeddings.py`** - sentence-transformers wrapper, caching
4. **`src/core_memory.py`** - Core Memory load/save/update logic
5. **`src/import_parser.py`** - Chunking strategies, format detection
6. **`src/synthesis.py`** - Clustering, synthesis orchestration
7. **`src/mcp_server.py`** - MCP tools implementation (including core memory tools)
8. **`src/cli.py`** - Click-based CLI (init, import, search, stats, core)
9. **`hooks/hooks.json`** - SessionStart, Stop hooks
10. **`agents/synthesizer.md`** - Synthesizer subagent prompt
11. **`skills/memory-awareness/SKILL.md`** - Auto-retrieval skill
12. **`commands/*.md`** - Slash commands (including core.md)
13. **`.claude-plugin/plugin.json`** - Plugin manifest
14. **`README.md`** - Documentation with install instructions, demo

---

## Key Implementation Notes

### For Claude Code Agent Building This

1. **Start with storage.py** - Get the data model right first
2. **Core Memory is special** - It's a markdown file, not in LanceDB. Load it on every SessionStart.
3. **Test embeddings early** - Make sure the model downloads correctly
4. **Import is critical for testing** - Build import_parser.py early so you can bootstrap test data
5. **Import should generate Core Memory** - After importing, synthesize an initial Core Memory
6. **Hooks need restart** - After modifying hooks.json, Claude Code needs full restart
7. **MCP server is the core interface** - All memory operations go through this
8. **Synthesizer is a subagent** - It runs within Claude Code, not as external process
9. **Keep summaries short** - Target ~100-200 tokens per summary for efficient retrieval
10. **Core Memory budget is ~2K tokens** - This is the always-loaded context ceiling
11. **Batch embeddings** - Always embed in batches for performance
12. **Config is optional** - Sensible defaults should work out of the box
13. **Error handling** - Graceful degradation if model download fails, DB is locked, etc.
14. **Core Memory file is human-editable** - Users can directly edit ~/.oubli/core_memory.md

### Dependencies (pyproject.toml)

```toml
[project]
name = "oubli"
version = "0.1.0"
description = "Fractal memory system for Claude Code"
requires-python = ">=3.10"
dependencies = [
    "lancedb>=0.4.0",
    "sentence-transformers>=2.2.0",
    "click>=8.0.0",
    "rich>=13.0.0",  # For CLI formatting
    "pyperclip>=1.8.0",  # For clipboard import
    "mcp>=1.0.0",  # MCP SDK
]

[project.scripts]
oubli = "oubli.cli:main"
```

---

## Success Metrics

### For Virality

- One-command install experience
- Works immediately after init
- Impressive first-run demo (import Claude.ai memory → instant context)
- Clear README with GIF showing before/after

### For Utility

- Retrieval latency < 100ms
- Relevant memories surface consistently
- Synthesis creates genuinely useful abstractions
- No annoying false positives or irrelevant context

---

## Tagline Options

- "Give Claude Code the memory it deserves"
- "Fractal memory for AI agents"
- "The memory Claude Code forgot to include"
- "Remember everything. Understand more."
