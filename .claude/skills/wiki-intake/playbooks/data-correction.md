# Playbook: data-correction

Step 2 (data-correction branch) — the mutation chain. A fact changed and needs to propagate through Data/, Knowledge/, Context, and Personal/Work as affected.

## Input

```yaml
content: <string>   # the capture, classified as `data-correction`
```

## Protocol

Executes **only on explicit operator mutation intent**: the capture itself IS a correction statement ("switched to X", "cancelled Y", "the value is now Z"). If mutation intent is inferred rather than stated, ask/confirm with the operator before touching anything.

Not every correction touches every layer. Scope it before acting:

1. **What changed?** State the old value and new value explicitly. "Stopped using Tool-X" = Tool-X status: active → discontinued. "New payment card ending NNNN" = card number updated (or new card issued).
2. **Where is this fact currently recorded?** Search each layer — a fact may live in zero, one, or multiple layers. Only layers that currently hold the old value need updating.
3. **What's the blast radius?** A single-tool change may only touch Data/ and a Knowledge/ file. An address change could ripple through multiple providers and Personal/ pages. Map the full chain before starting edits.
4. **Which edits are appends vs. substance changes?** Appending new information to Knowledge/ is autonomous. Editing existing substance requires human approval. Know which you're doing before you start.

**Execution steps:**

1. **Identify the domain** — which Wiki area does this correction touch? Match it to a context page, `{workspace_root}/Wiki/Contexts/<area>-context.md`.
2. **Load the domain's context page** — understand current state.
3. **Identify affected files** (check all layers): Data/ records (if structured data exists), Knowledge/ files (if the correction affects narrative knowledge), Context page (if working understanding needs updating), Personal/Work pages (downstream, stewarded last).
4. **Apply the correction** through the chain:
   - Data/ → update frontmatter fields with `Edit`
   - Knowledge/ → read the file's `update` field first. `append`: add the new information as a dated entry, existing text unchanged, then set `updated`. `replace` or `never`: halt and flag for human approval (Stop rule) — `replace` takes an in-place rewrite she approves, `never` takes a successor file.
   - Context page → update through the `context-page` skill if working understanding shifted
   - Personal/Work → targeted `Edit` only (autonomous stewardship rules apply)
5. **Report what was updated** across all layers.

## Output

```yaml
layers_touched: [Data | Knowledge | Context | Personal/Work]
summary: <string>
```

## Stop rule

If the correction would require editing existing substance in a Knowledge/ file (not appending), or the file's `update` is not `append`, halt and flag for human approval.

## What this playbook does NOT do

- Does NOT execute on inferred mutation intent — ask/confirm first.
- Does NOT edit existing Knowledge/ substance — append only; substance edits halt for approval.
- Does NOT touch layers that don't currently hold the old value.
