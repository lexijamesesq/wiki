A Claude Code system that runs an agent-maintained knowledge base inside an Obsidian vault. Every capture passes through a single gatekeeper that files, queues, or discards it; an operator-judgment queue holds what the gatekeeper will not decide alone; and machine-parseable contracts derive their own lint rules instead of drifting from prose. An unattended maintenance lane runs under dead-man monitoring behind layered publication guards, orchestrated through Claude Code skills.

## Installation

Clone the repo, then set up the Claude Code directory:

```
mv claude .claude
```

Copy the sample config and fill in your values:

```
cp CLAUDE.sample.md CLAUDE.md
```

### Required configuration

| Field | Location | What to set |
|---|---|---|
| `workspace_root` | Global Claude Code config | Your vault's root path. Every `{workspace_root}` placeholder in this repo resolves against it, and this repo must be cloned in as `Wiki/` at that root. |
| Architecture doc link | `CLAUDE.md` § Header | Your own architecture doc — space structure, linking mechanisms, hub disposition |
| Human-facing surface | `CLAUDE.md` § Design Philosophy | The surface you browse by hand, and its stewardship trigger |
| Intake skill name | `CLAUDE.md` § Intake | Your single entry point for Wiki-axis content |
| Consolidation threshold | `CLAUDE.md` § Health Metrics | The `Knowledge/` file size that triggers a human-approved review |
| Automated lane scope | `CLAUDE.md` § Decision Authority | Your automated lanes, and the exact scope each may write to |
| Queue taxonomy | `CLAUDE.md` § Self-Management | Your `Queue/` item kinds, and the name of your triage verb |
| Freshness window | `CLAUDE.md` § Freshness Signals | Your staleness window in days, measured from `verified` or `updated` |
| Instance-data roster | `CLAUDE.md` § Key Files | Your real names and employers roster — gitignored, referenced by the taxonomy contract, never restated inline |

### Optional configuration

| Field | Location | What to set |
|---|---|---|
| Migration doc link | `CLAUDE.md` § Knowledge Sources | Your migration or onboarding doc, if you have one |
| Specialized handlers | `CLAUDE.md` § Intake | Your own intake handlers, such as a recurring-meeting capture skill |
| Pending-work log | `CLAUDE.md` § Pending Work | Genuinely pending infrastructure work only |

### Dependencies

- **Claude Code**, with this repo's skills installed as a project-level skills directory (`mv claude .claude`).
- **An Obsidian vault**, or a plain folder tree. Wikilinks and frontmatter-driven tag queries are the real dependency, not Obsidian itself.
- **Sibling content folders** — the skills expect `Knowledge/`, `Data/`, `Contexts/`, `Attachments/`, and `Queue/` beside this repo's tracked machinery. None are tracked here; they are your content.
- **The companion [dotty](https://github.com/lexijamesesq/dotty) repo** — it ships the four ingress skills this system runs on, plus the lint engine the contracts feed. Install both.
- **A session harness (optional)** — these skills run standalone. A broader orchestration layer can wrap them, but nothing here requires one beyond Claude Code itself.

## What's Included

### Ingress

How content gets in. Every capture passes through the gatekeeper before anything is written. These four skills ship in the companion [dotty](https://github.com/lexijamesesq/dotty) repo, not here — install both.

| Artifact | Type | What it does |
|----------|------|--------------|
| `/wiki-intake` | Skill (dotty) | Classifies a capture's intent, resolves its destination, and hands it to the gatekeeper |
| `/gatekeeper` | Skill (dotty) | Routes every candidate to a terminal disposition — file, queue, or discard — through a mode × trust × kind matrix |
| `/capture-meeting` | Skill (dotty) | Captures a recurring meeting, gating autonomous filing on whether the source is registered |
| `/queue` | Skill (dotty) | Creates pending-decision items and runs the menu-guided triage flow |

### Maintenance

Runs unattended on a schedule, and writes nothing outside `Queue/`.

| Artifact | Type | What it does |
|----------|------|--------------|
| `/maintenance-triage` | Skill | Reads staged lint findings, then splits deterministic envelope fixes from the judgments that must land in the queue |

### Contracts

Each contract carries a Parsing Contract, so a lint engine derives its rules mechanically at runtime rather than hardcoding a second copy. That engine — the `/lint-knowledge` skill and its `filing-validator` agent — also ships in dotty.

| Artifact | Type | What it does |
|----------|------|--------------|
| `spec/structural-contract.md` | Contract | Defines the file envelope: required frontmatter, valid tags, discoverability |
| `spec/tag-taxonomy.md` | Contract | Closes the tag namespaces, and sets a growth threshold and depth limit for each |
| `spec/handoff-contracts.md` | Contract | Says which skill owns which write, so two skills never file the same thing |
| `spec/lint-surface.md` | Contract | Lists the lint rules the engine derives from the three contracts above |

## Configuration

The system separates what you configure from what skills handle.

**You configure:**
- `CLAUDE.md` — filled in from `CLAUDE.sample.md`'s `TODO:` markers: architecture doc link, intake skill name, size thresholds, automated-lane scope
- `spec/tag-taxonomy.md` — only if your namespaces or growth thresholds differ from the defaults

**Skills handle:**
- Candidate disposition, through the gatekeeper's mode × trust × kind matrix
- Tag-taxonomy and structural-contract enforcement
- Lint-rule derivation from each contract's own Parsing Contract
- Dead-man monitoring for the maintenance lane

See `CLAUDE.sample.md` for the full configuration contract with placeholder values.

## Usage

### Filing new content

```
/wiki-intake
```

Classifies intent and routes: knowledge candidates go to the gatekeeper, explore captures become queue items, and data corrections propagate through the affected layers.

### Recurring meetings

```
/capture-meeting <meeting-name>
```

Registered meetings dual-write a per-area rolling log and emit candidates to the gatekeeper. Unregistered meetings are routed only.

### Operator-judgment queue

```
/queue triage
```

Menu-guided triage of pending items, scoped or all.

## How It Works

Content enters through one path and narrows. An intake skill classifies a capture's intent; the gatekeeper resolves it against a disposition matrix indexed by mode (interactive or automated), trust (registered or unregistered source), and kind; only then does a write happen. No extractor chooses its own destination, so a new capture surface never adds a new way to write to the vault.

The contracts under `spec/` are the schema, and each publishes a Parsing Contract describing how to read it. The lint engine reads those at runtime and derives its rules from them, so a rule cannot disagree with the spec that produced it — there is only ever one copy.

The design bet: a wiki that reads at write-time — compiled, curated, kept "clean" — drifts silently the moment a source changes underneath it, because nothing forces a re-check of the compilation. This system instead keeps faithful, source-attributed captures and synthesizes at query time, so every session load is a fresh read of current state rather than a cached summary. Mutation is append-biased by design: editing existing substance is the primary corruption vector, so new information appends alongside old, and destructive consolidation requires a human in the loop.

The maintenance lane runs unattended on a schedule and writes nothing outside `Queue/`. Dead-man monitoring watches the lane itself, so a silently stopped job surfaces as a finding rather than as months of nothing happening.

## Customization

The system ships tuned for an Obsidian vault, a meeting registry, and the companion dotty skills. To adapt it:

- **New meeting types:** the companion `/capture-meeting` skill gates autonomous filing on a registry. Copy [meeting-registry.sample.json](https://github.com/lexijamesesq/dotty/blob/main/.claude/skills/capture-meeting/meeting-registry.sample.json) from dotty, then add an entry to promote a meeting to dual-write.
- **New tag namespaces:** `spec/tag-taxonomy.md` sets a growth threshold per namespace — some auto-create, some need confirmation, and some are procedural, requiring downstream consumers to be updated.
- **Disposition tuning:** dotty's [calibration-surface.md](https://github.com/lexijamesesq/dotty/blob/main/.claude/skills/gatekeeper/calibration-surface.md) is the canonical home for the dimensions, thresholds, and disposition matrix. Amend there; every consumer skill references it rather than re-deriving its own copy.
- **Without Obsidian:** the skills need wikilinks and frontmatter-driven tag queries, not Obsidian itself. A plain folder tree with the same structure works.

## Security

Review skills before installing. They load into Claude's context and execute with your permissions. Audit the contents of `claude/skills/` before use.

Writes are scoped — `/maintenance-triage`, for example, writes nothing outside `Queue/`. `.gitleaks.toml`, `.pre-commit-config.yaml`, and `.track-list-guard.sh` ship as the same publication guards this instance runs under: a track-list allow-list, a secret and PII scan, and a required-file presence check, on top of the standard pre-commit-hooks set.

## License

MIT. See [LICENSE](LICENSE).
