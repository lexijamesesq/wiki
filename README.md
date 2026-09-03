A Claude Code system that keeps a personal knowledge base in an Obsidian vault and maintains it. Every capture is routed by one skill, which decides whether to file it, hold it for a human decision, or drop it — so a new way to capture content never becomes a new way to write to the vault. The specs that define a valid note also generate the lint rules that enforce them, and a scheduled job cleans up what it safely can, orchestrated through Claude Code skills.

## Installation

This repo carries the machinery only — the skills, the contracts they derive lint rules from, and this repo's own publication guards. Your actual knowledge (`Knowledge/`, `Data/`, `Contexts/`, `Attachments/`, `Queue/`) lives in your Obsidian vault, addressed by `{workspace_root}` — the two are decoupled, this repo can live anywhere on disk. The companion [dotty](https://github.com/lexijamesesq/dotty) repo carries the session harness that can wrap these skills; nothing here requires it.

Clone the repo. `.claude/` ships tracked and committed — review its contents (see Security below) before opening the directory in Claude Code.

Copy the sample config and fill in your values:

```
cp .claude/instance.sample.md .claude/instance.md
```

### Required configuration

| Field | Location | What to set |
|-------|----------|-------------|
| `workspace_root` | Global Claude Code config | Your vault's root path. Every `{workspace_root}` placeholder in this repo's skills resolves against it, to find your vault's `{workspace_root}/Wiki/Knowledge/`, `{workspace_root}/Wiki/Data/`, etc. — independent of where this repo itself is checked out. |
| Architecture doc link | .claude/instance.md > Header | Your own architecture doc — space structure, linking mechanisms, hub disposition |
| Human-facing surface | .claude/instance.md > Design Philosophy | The surface you browse by hand |
| Stewardship trigger | .claude/instance.md > Human-Facing Page Stewardship | What causes Claude to re-check those pages for stale facts |
| Intake skill name | .claude/instance.md > Intake | Your single entry point for Wiki-axis content |
| Consolidation threshold | .claude/instance.md > Health Metrics | The `Knowledge/` file size that triggers a human-approved review |
| Automated lane scope | .claude/instance.md > Decision Authority | Your automated lanes, and the exact scope each may write to |
| Queue taxonomy | .claude/instance.md > Self-Management | Your `Queue/` item kinds, and the name of your triage verb |
| Freshness window | .claude/instance.md > Freshness signals | Your staleness window in days, measured from `verified` or `updated` |
| Instance-data roster | .claude/instance.md > Key Files | Your real names and employers roster — gitignored, referenced by the taxonomy contract, never restated inline |

### Optional configuration

| Field | Location | What to set |
|-------|----------|-------------|
| Migration doc link | .claude/instance.md > Knowledge Sources | Your migration or onboarding doc, if you have one |
| Specialized handlers | .claude/instance.md > Intake | Your own intake handlers, such as a recurring-meeting capture skill |
| Pending-work log | .claude/instance.md > Pending Work | Genuinely pending infrastructure work only |

### Dependencies

- **Claude Code** — this repo's skills install as a project-level skills directory (`.claude/`, tracked and committed).
- **An Obsidian vault** *(optional)* — the skills read wikilinks and frontmatter tag queries, which Obsidian provides.
- **Vault content folders** — the skills expect `Knowledge/`, `Data/`, `Contexts/`, `Attachments/`, and `Queue/` under `{workspace_root}/Wiki/` in your vault. None are tracked here; they are your content, and this repo doesn't need to live next to them.
- **A session harness** *(optional)* — these skills run standalone. A broader orchestration layer — such as the companion [dotty](https://github.com/lexijamesesq/dotty) repo's session skills — can wrap them, but nothing here requires one beyond Claude Code itself.

## What's Included

### Ingress

How content gets in. Every capture passes through the gatekeeper before anything is written.

| Artifact | Type | What it does |
|----------|------|--------------|
| `/wiki-intake` | Skill | The single front door for Wiki-axis content — classifies intent and routes to the gatekeeper, the queue, or the data-correction path. At `.claude/skills/wiki-intake/` |
| `/gatekeeper` | Skill | Resolves every candidate to file, queue, or discard through the mode × trust × kind matrix — the only skill that writes into the knowledge layer. At `.claude/skills/gatekeeper/` |
| `/capture` | Skill | The mid-session capture verb — extracts knowledge candidates from the live conversation and hands every one to the gatekeeper. At `.claude/skills/capture/` |
| `/capture-meeting` | Skill | Captures a recurring meeting, gating autonomous filing on whether the source is registered. At `.claude/skills/capture-meeting/` — its consumer is the Pi lane, which resolves vault-resident skills |
| `/router` | Skill | Sorts Inbox captures and delivers each to its destination's intake. At `.claude/skills/router/` |
| `/queue` | Skill | Creates operator-judgment queue items and runs the menu-guided triage. At `.claude/skills/queue/` |

### Maintenance

The scheduled cleanup pass, plus the per-session maintenance operations.

| Artifact | Type | What it does |
|----------|------|--------------|
| `/knowledge-layer` | Skill | The per-session domain expert — freshness scans, hygiene anti-pattern checks, envelope-enforced filing through the lint gate, index sync, hub cross-reference. At `.claude/skills/knowledge-layer/` |
| `/lint-knowledge` | Skill + Script | The lint engine — derives its rules from the contracts at runtime, scans full-corpus on a schedule or single-file at filing time, and reports findings without auto-fixing. At `.claude/skills/lint-knowledge/` |
| `/maintenance-triage` | Skill | Reads staged lint findings, then separates the mechanical fixes it can apply from the judgments that must wait for you. At `.claude/skills/maintenance-triage/` |

### Contracts

Each contract declares how to read it, so the lint engine derives its rules from the spec at runtime. That engine — the `/lint-knowledge` skill and its `lint.py` script, run periodically full-corpus or single-file at filing time (`--filing`) — ships here, at `.claude/skills/lint-knowledge/`.

| Artifact | Type | What it does |
|----------|------|--------------|
| `spec/knowledge-contract.md` | Contract | The consolidated rulebook. Part I closes the tag namespaces with growth thresholds and depth limits; Part II defines the file envelope (required frontmatter, valid tags, discoverability); Part III says which skill owns which write, so two skills never file the same thing; Part IV lists the lint rules; Part V is the parsing contract the engine derives them from |
| `spec/tag-taxonomy-rosters.md` | Roster (local, untracked) | The real-name rosters (people, employers, area top-levels) — split from the contract so the public shape carries no PII; gitignored, you create your own |
| `spec/calibration-surface.md` | Contract | The ingress judgment tables — disposition philosophy, the four dimensions, the mode × trust × kind matrix, destination resolution, worked examples |
| `spec/integration-modes.md` | Contract | Per-destination write discipline — evolution vs current-truth, write shape × authority, and the activation-gated validated-mutation path |

## Configuration

The system separates what you configure from what skills handle.

**You configure:**
- `.claude/instance.md` — filled in from `.claude/instance.sample.md`'s `TODO:` markers: architecture doc link, intake skill name, size thresholds, automated-lane scope
- `spec/knowledge-contract.md` Part I — only if your namespaces or growth thresholds differ from the defaults

**Skills handle:**
- Candidate disposition, through the gatekeeper's mode × trust × kind matrix
- Tag and envelope enforcement per the knowledge contract
- Lint-rule derivation from each contract's own Parsing Contract
- Dead-man monitoring for the maintenance lane

See `.claude/instance.sample.md` for the full configuration contract with placeholder values.

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

```
  session captures     meetings (automated lane)     everything else
     /capture              /capture-meeting            /wiki-intake
         └──────────────────────┼─────────────────────────┘
                                ▼
                          /gatekeeper
                   mode × trust × kind matrix
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
        file                  queue                discard
   Knowledge/ Data/       Queue/ — waits         logged, with
   Contexts/ + logs        for a human            the reason
```

The contracts under `spec/` are the schema, and each publishes a Parsing Contract describing how to read it. The lint engine reads those at runtime and derives its rules from them, so a rule cannot disagree with the spec that produced it — there is only ever one copy.

The design bet: a wiki that reads at write-time — compiled, curated, kept "clean" — drifts silently the moment a source changes underneath it, because nothing forces a re-check of the compilation. This system instead keeps faithful, source-attributed captures and synthesizes at query time, so every session load is a fresh read of current state rather than a cached summary. Mutation is append-biased by design: editing existing substance is the primary corruption vector, so new information appends alongside old, and destructive consolidation requires a human in the loop.

The maintenance lane runs unattended on a schedule. A heartbeat check watches the lane itself, so a job that stops silently surfaces as a finding rather than as months of nothing happening.

## Customization

The system ships tuned for an Obsidian vault, a meeting registry, and the companion dotty skills. To adapt it:

- **New meeting types:** the `/capture-meeting` skill gates autonomous filing on a registry. Copy [meeting-registry.sample.json](.claude/skills/capture-meeting/meeting-registry.sample.json) from this repo, then add an entry to promote a meeting to dual-write.
- **New tag namespaces:** `spec/knowledge-contract.md` Part I sets a growth threshold per namespace — some auto-create, some need confirmation, and some are procedural, requiring downstream consumers to be updated.
- **Disposition tuning:** [spec/calibration-surface.md](spec/calibration-surface.md) is the canonical home for the dimensions, thresholds, and disposition matrix. Amend there; every consumer skill references it rather than re-deriving its own copy.
- **Without Obsidian:** the skills need wikilinks and frontmatter-driven tag queries, not Obsidian itself. A plain folder tree with the same structure works.

## Security

Review skills before installing. They load into Claude's context and execute with your permissions. Audit the contents of `.claude/skills/` before use.

Writes are scoped — `/maintenance-triage`, for example, writes nothing outside `Queue/`. `.gitleaks.toml`, `.pre-commit-config.yaml`, and `.track-list-guard.sh` ship as the same publication guards this instance runs under: a track-list allow-list, a secret and PII scan, and a required-file presence check, on top of the standard pre-commit-hooks set.

## License

MIT. See [LICENSE](LICENSE).
