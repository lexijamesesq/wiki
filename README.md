# wiki

A Claude Code system that keeps a personal knowledge base in an Obsidian vault and maintains it. Every capture is routed by one skill, which decides whether to file it, hold it for a human decision, or drop it — so a new way to capture content never becomes a new way to write to the vault. Every knowledge file declares four frontmatter fields — a one-line description, how its body may change, related files, and the date it last changed — and a lint tool checks them.

## Installation

This repo carries the machinery only — the skills, the specs they follow, and this repo's own publication guards. Your actual knowledge (`Knowledge/`, `Data/`, `Contexts/`, `Attachments/`, `Queue/`) lives in your Obsidian vault, addressed by `{workspace_root}` — the two are decoupled, this repo can live anywhere on disk. The companion [dotty](https://github.com/lexijamesesq/dotty) repo carries the session harness that can wrap these skills; nothing here requires it.

Clone the repo. `.claude/` ships tracked and committed — review its contents (see Security below) before opening the directory in Claude Code.

Copy the sample config and fill in your values:

```bash
cp .claude/instance.sample.md .claude/instance.md
```

**Or install it as a Claude Code plugin.** This repo root is also the `wiki` plugin — the same skills, served to every session in a profile from Claude Code's plugin cache instead of from a checkout:

```bash
claude plugin marketplace add lexijamesesq/wiki
claude plugin install wiki@wiki
claude plugin enable wiki@wiki
```

The manifest lives at `.claude-plugin/` and points the plugin at `.claude/skills/`, so the skills stay where the project-level layout and the CI already read them. A plugin install copies the tracked tree into the cache; editing this checkout changes nothing a session loads until `claude plugin update wiki@wiki` runs. The plugin ships the skills only: the values they resolve at runtime (`{workspace_root}` and `projects_root`) come from your global Claude Code Configuration block, not from the cache, and `.claude/instance.md` — the stewardship rules for a checkout-scoped session — is gitignored and stays with a checkout.

### Required configuration

| Field | Location | What to set |
| ------- | ---------- | ------------- |
| `workspace_root` | Global Claude Code config | Your vault's root path. Every `{workspace_root}` placeholder in this repo's skills resolves against it, to find your vault's `{workspace_root}/Wiki/Knowledge/`, `{workspace_root}/Wiki/Data/`, etc. — independent of where this repo itself is checked out. |
| `projects_root` | Global Claude Code config | Your projects folder. Skills find a project by path — a folder under it holding a `CLAUDE.md` — and place project-hosted knowledge in its `Knowledge/` type folders. |
| Architecture doc link | .claude/instance.md > Header | Your own architecture doc — space structure, linking mechanisms, hub disposition |
| Human-facing surface | .claude/instance.md > Design Philosophy | The surface you browse by hand |
| Stewardship trigger | .claude/instance.md > Human-Facing Page Stewardship | What causes Claude to re-check those pages for stale facts |
| Intake skill name | .claude/instance.md > Intake | Your single entry point for Wiki-axis content |
| Consolidation threshold | .claude/instance.md > Health Metrics | The `Knowledge/` file size that triggers a human-approved review |
| Automated lane scope | .claude/instance.md > Decision Authority | Your automated lanes, and the exact scope each may write to |
| Queue taxonomy | .claude/instance.md > Self-Management | Your `Queue/` item kinds, and the name of your triage verb |
| Freshness window | .claude/instance.md > Freshness signals | Your staleness window in days, measured from `updated` |

### Optional configuration

| Field | Location | What to set |
| --- | --- | --- |
| Migration doc link | .claude/instance.md > Knowledge Sources | Your migration or onboarding doc, if you have one |
| Pending-work log | .claude/instance.md > Pending Work | Genuinely pending infrastructure work only |

### Dependencies

- **Claude Code** — this repo's skills install as a project-level skills directory (`.claude/`, tracked and committed) or as the `wiki` plugin (see Installation).
- **An Obsidian vault** *(optional)* — `related` links are wikilinks, which Obsidian renders and keeps current across renames.
- **Vault content folders** — the skills expect `Knowledge/`, `Data/`, `Contexts/`, `Attachments/`, and `Queue/` under `{workspace_root}/Wiki/` in your vault. None are tracked here; they are your content, and this repo doesn't need to live next to them.
- **A session harness** *(optional)* — these skills run standalone. A broader orchestration layer — such as the companion [dotty](https://github.com/lexijamesesq/dotty) repo's session skills — can wrap them, but nothing here requires one beyond Claude Code itself.

## What's Included

### Ingress

How content gets in. Every capture passes through the gatekeeper before anything is written.

| Artifact | Type | What it does |
| ---------- | ------ | -------------- |
| `/wiki-intake` | Skill | Takes Wiki-axis content handed over directly — classifies intent and routes to the gatekeeper, the queue, or the data-correction chain, which it owns. At `.claude/skills/wiki-intake/` |
| `/gatekeeper` | Skill | Resolves every candidate to file, queue, or discard through the mode × trust × kind matrix — the only skill that writes into the knowledge layer. A session files something mid-session with `/gatekeeper assess single`. At `.claude/skills/gatekeeper/` |
| `/router` | Skill | Sorts Inbox captures and delivers each to its destination's intake; knowledge goes to the gatekeeper. At `.claude/skills/router/` |
| `/queue` | Skill | Creates operator-judgment queue items and runs the menu-guided triage. At `.claude/skills/queue/` |

### Maintenance

The per-session maintenance operations and the tools they share.

| Artifact | Type | What it does |
| ---------- | ------ | -------------- |
| `/knowledge-description` | Skill + Scripts | Writing a file's description; the describe tool, which prints one line per file in a folder; and `contract_lint.py`, which checks files against the contract. At `.claude/skills/knowledge-description/` |
| `/context-page` | Skill | Keeps a Wiki area's context page current when a session learns something durable. At `.claude/skills/context-page/` |
| `/knowledge-layer` | Skill | The closeout domain expert — hygiene checks that respect each file's update mode, handing new synthesis to the gatekeeper, and a contract lint of the files a session touched. At `.claude/skills/knowledge-layer/` |
| `/lint-knowledge` | Skill | Runs the contract lint over a project, the Wiki, or the whole vault and reports, without fixing. At `.claude/skills/lint-knowledge/` |

### Contracts

| Artifact | Type | What it does |
| ---------- | ------ | -------------- |
| `spec/knowledge-files.md` | Contract | The knowledge-file contract: four frontmatter fields (`description`, `update`, `related`, `updated`), the three update modes (`append`, `replace`, `never`), and the type folders |
| `spec/knowledge-contract.md` | Contract | The earlier tag-based rulebook, superseded by `spec/knowledge-files.md`; no skill here reads it |
| `spec/calibration-surface.md` | Contract | The ingress judgment tables — disposition philosophy, the four dimensions, the mode × trust × kind matrix, destination resolution, worked examples |
| `spec/integration-modes.md` | Contract | Per-destination write discipline — evolution vs current-truth, write shape × authority, and the activation-gated validated-mutation path |

## Configuration

The system separates what you configure from what skills handle.

**You configure:**

- `.claude/instance.md` — filled in from `.claude/instance.sample.md`'s `TODO:` markers: architecture doc link, intake skill name, size thresholds

**Skills handle:**

- Candidate disposition, through the gatekeeper's mode × trust × kind matrix
- Frontmatter per `spec/knowledge-files.md`, checked by `contract_lint.py`
- Respecting each file's update mode on every write

See `.claude/instance.sample.md` for the full configuration contract with placeholder values.

## Usage

### Filing new content

```text
/wiki-intake
```

Classifies intent and routes: knowledge candidates go to the gatekeeper, explore captures become queue items, and data corrections propagate through the affected layers.

### Filing from a session

```text
/gatekeeper assess single
```

The session hands one self-contained candidate (content, kind, provenance, trust, mode) to the gatekeeper, which places, files and lints it. At closeout, `/knowledge-layer` query-and-file does the same for the session's synthesis.

### Operator-judgment queue

```text
/queue triage
```

Menu-guided triage of pending items, scoped or all.

## How It Works

Content enters through one path and narrows. An intake skill classifies a capture's intent; the gatekeeper resolves it against a disposition matrix indexed by mode (interactive or automated), trust (registered or unregistered source), and kind; only then does a write happen. No extractor chooses its own destination, so a new capture surface never adds a new way to write to the vault.

```text
  session / closeout        Inbox              everything else
  query-and-file           /router              /wiki-intake
         └──────────────────────┼─────────────────────────┘
                                ▼
                          /gatekeeper
                   mode × trust × kind matrix
          ┌─────────────────────┼─────────────────────┐
          ▼                     ▼                     ▼
        file                  queue                discard
   Knowledge/ Data/       Queue/ — waits         logged, with
   Contexts/               for a human            the reason
```

`spec/knowledge-files.md` is the schema: four frontmatter fields and three update modes. A file's `update` field is the instruction every writer reads before changing it — `append` adds only, `replace` rewrites in place with no banners, `never` takes a successor file — and the gatekeeper appends only to `append` files. `contract_lint.py` checks the frontmatter.

The design bet: a wiki that reads at write-time — compiled, curated, kept "clean" — drifts silently the moment a source changes underneath it, because nothing forces a re-check of the compilation. This system instead keeps faithful, source-attributed captures and synthesizes at query time, so every session load is a fresh read of current state rather than a cached summary. Mutation is governed per file: editing existing substance is the primary corruption vector, so the gatekeeper adds new information only to files declared `append`, and a rewrite of a `replace` file needs a human in the loop.

## Customization

The system ships tuned for an Obsidian vault and the companion dotty skills. To adapt it:

- **New type folders:** a project may add folders beside the five base type folders in its `Knowledge/` (`spec/knowledge-files.md` › Structure).
- **Disposition tuning:** [spec/calibration-surface.md](spec/calibration-surface.md) is the canonical home for the dimensions, thresholds, and disposition matrix. Amend there; every consumer skill references it rather than re-deriving its own copy.
- **Without Obsidian:** the skills need frontmatter and wikilink text, not Obsidian itself. A plain folder tree with the same structure works.

## Security

Review skills before installing. They load into Claude's context and execute with your permissions. Audit the contents of `.claude/skills/` before use.

No skill pre-approves a file tool, so every vault read and write runs under the session's own permissions. `.gitleaks.toml`, `.pre-commit-config.yaml`, and `.track-list-guard.sh` ship as the same publication guards this instance runs under: a track-list allow-list, a secret and PII scan, and a required-file presence check, on top of the standard pre-commit-hooks set.

## License

MIT. See [LICENSE](LICENSE).
