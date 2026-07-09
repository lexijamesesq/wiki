A Claude Code system that runs an agent-maintained knowledge base inside an Obsidian vault — every capture passes through a single gatekeeper that files, queues, or discards it, an operator-judgment queue holds what the gatekeeper won't decide alone, and machine-parseable contracts derive their own lint rules instead of drifting from prose. An unattended maintenance lane with dead-man monitoring and layered publication guards, orchestrated through Claude Code skills.

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

| TODO marker | Section | What to set |
|---|---|---|
| Architecture doc reference | Header | Link your own architecture doc — space structure, linking mechanisms, hub disposition |
| Vault-root config key | Header | Define `workspace_root` (your vault's root path) in your global Claude Code config — every `{workspace_root}` placeholder in this repo resolves against it, and this repo must be cloned in as `Wiki/` at that root |
| Human-facing surface name | Design Philosophy | Name your human-facing surface and its stewardship trigger, if you use one |
| Router/intake skill name | Intake | Name your single entry point for Wiki-axis content |
| Consolidation size threshold | Health Metrics | Your Knowledge/ file size threshold before a human-approved review |
| Automated lane scope | Decision Authority | Name your automated lanes and their exact write scope |
| Queue taxonomy + triage verb | Self-Management | Define your Queue/ item kinds and name your triage verb |
| Freshness window | Freshness Signals | Your staleness window (e.g. 90 days) from `verified`/`updated` |
| Instance-data roster | Key Files | Your real names/employers roster — gitignored, referenced by the taxonomy contract but never restated inline |

### Optional configuration

| TODO marker | Section | What to set |
|---|---|---|
| Migration/onboarding doc reference | Knowledge Sources & Prioritization | Link your migration doc, if you have one |
| Specialized intake handlers | Intake | Your own specialized handlers (e.g. a recurring-meeting capture skill), if any |
| Pending-work log | Pending Work | Genuinely-pending infrastructure work only |

### Dependencies

- **Claude Code**, with the skills under `claude/` installed as a project-level skills directory (`mv claude .claude`).
- **An Obsidian vault** — or a plain folder tree; wikilinks and frontmatter-driven tag queries are the actual dependency, not Obsidian itself. Clone this repo in as `Wiki/` at your vault's root — this repo's own specs write fully-qualified paths like `{workspace_root}/Wiki/Knowledge/` and `{workspace_root}/Wiki/Queue/` (see `spec/handoff-contracts.md`), so those and this README's flat `Queue/` below (repo-root-relative) name the same folder once cloned in place. Set `workspace_root` per Required configuration, above. The skills expect `Knowledge/`, `Data/`, `Contexts/`, `Attachments/`, and `Queue/` folders alongside this repo's tracked machinery — none of those are tracked here; they're your content.
- **Companion skills** — this repo ships one skill (`/maintenance-triage`). The other skills that operate on this system — `/gatekeeper`, `/wiki-intake`, `/queue`, `/capture-meeting` — ship in the companion [dotty](https://github.com/lexijamesesq/dotty) repo as global Claude Code skills. Install both repos for the full system.
- **A session harness (optional)** — these skills run standalone. A broader orchestration layer can wrap them, but nothing here requires one beyond Claude Code itself.

## What's Included

### Skill

| Skill | What it does |
|---|---|
| `/maintenance-triage` | Unattended maintenance-lane judgment pass — reads staged lint findings, splits deterministic envelope fixes from genuinely-stuck judgments that land in the queue. |

### Companion skills (from [dotty](https://github.com/lexijamesesq/dotty))

The full system uses these global skills, which ship in the companion repo:

| Skill | What it does |
|---|---|
| `/gatekeeper` | The single router every candidate passes through before it's filed, queued, or discarded, via a mode x trust x kind disposition matrix. |
| `/wiki-intake` | Single entry point for knowledge-axis captures — classifies intent, resolves destination, hands off to the gatekeeper. |
| `/queue` | The operator-judgment queue — creates pending-decision items and runs the menu-guided triage flow. |
| `/capture-meeting` | Structured capture for recurring meetings, with a registered/unregistered trust distinction that gates autonomous filing. |

### Contracts

Each contract carries a Parsing Contract so a lint engine — [dotty](https://github.com/lexijamesesq/dotty)'s `/lint-knowledge` skill (`lint.py`) plus its `filing-validator` agent — can derive rules mechanically at runtime instead of hardcoding a second copy of them. Neither ships in this repo; both are the public companion.

| Path | What it is |
|---|---|
| `spec/structural-contract.md` | Required frontmatter, tag validity, discoverability — the file envelope. |
| `spec/tag-taxonomy.md` | Closed tag namespaces, growth thresholds, depth limits. |
| `spec/handoff-contracts.md` | Cross-skill filing contracts — which skill owns which write. |
| `spec/lint-surface.md` | Machine-parseable lint rules derived from the contracts above. |

## Configuration

The system separates what you configure from what skills handle.

**You configure:** `CLAUDE.md`, filled in from `CLAUDE.sample.md`'s `TODO:` markers — architecture doc link, intake skill name, size thresholds, automated-lane scope. `spec/tag-taxonomy.md`, if your own namespaces or growth thresholds differ from the defaults.

**Skills handle:** Candidate disposition via the gatekeeper's mode x trust x kind matrix, tag-taxonomy and structural-contract enforcement, lint-rule derivation from each contract's own Parsing Contract, and dead-man monitoring for the maintenance lane.

See `CLAUDE.sample.md` for the full configuration contract with placeholder values.

## Usage

### Filing new content

```
/wiki-intake
```

Classifies intent and routes: knowledge-intent candidates go to the gatekeeper, explore/triage captures become queue items, data corrections propagate through the affected layers.

### Recurring meetings

```
/capture-meeting <meeting-name>
```

Registered meetings dual-write a per-area rolling log plus candidates into the gatekeeper; unregistered meetings are routed-only.

### Operator-judgment queue

```
/queue triage
```

Menu-guided triage of pending items, scoped or all.

## How It Works

A Claude Code-driven knowledge base that maintains itself: one gatekeeper decides where every incoming piece of information goes, a human-judgment queue catches everything the gatekeeper can't or won't decide alone, and a set of machine-parseable contracts generate their own lint enforcement rather than drifting out of sync with prose documentation. An unattended maintenance lane runs on a schedule, with dead-man monitoring so a silently-stopped job surfaces immediately instead of going unnoticed.

The design bet: a wiki that reads at write-time — compiled, curated, kept "clean" — drifts silently the moment a source changes underneath it, because nothing forces a re-check of the compilation. This system instead keeps faithful, source-attributed captures and synthesizes at query time, so every session load is a fresh read of current state, not a cached summary that might be stale. Mutation is append-biased by design: editing existing substance is the primary corruption vector, so new information appends alongside old, and destructive consolidation requires a human in the loop.

## Customization

- **New meeting types:** The companion `/capture-meeting` skill uses a meeting registry to gate autonomous filing. Copy its sample registry and add an entry to promote a meeting to dual-write. See the [dotty](https://github.com/lexijamesesq/dotty) repo for details.
- **New tag namespaces:** `spec/tag-taxonomy.md` documents growth thresholds per namespace — some auto-create, some need confirmation, some are procedural and require updating downstream consumers.
- **Disposition judgment tuning:** The companion `/gatekeeper` skill carries a calibration surface that defines the dimensions, thresholds, and disposition matrix. See the [dotty](https://github.com/lexijamesesq/dotty) repo for details.
- **Without Obsidian:** The skills don't require Obsidian itself — wikilinks and frontmatter-driven tag queries are the actual dependency, so a plain folder tree with the same structure works.

## Security

Review skills before installing. They load into Claude's context and execute with your permissions. Audit the contents of `claude/skills/` before use.

Writes are scoped — the maintenance-triage skill, for example, writes nothing outside `Queue/`. `.gitleaks.toml`, `.pre-commit-config.yaml`, and `.track-list-guard.sh` ship as the same publication guards this instance runs under: a track-list allow-list, a secret/PII scan, and required-file presence, on top of the standard pre-commit-hooks set.

## License

MIT. See [LICENSE](LICENSE).
