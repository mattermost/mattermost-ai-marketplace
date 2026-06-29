# teamsecure

Adversarial security review for code changes. Runs a two-role pipeline — a **paranoid
finder** that aggressively surfaces anything suspicious, and a **critical validator**
that verifies each finding until it is provably a true or false positive — and emits a
structured findings list.

It is the security sibling of `teamimplement`: it can run on its own, and `teamimplement`
spawns its two agents directly so freshly-implemented code is security-reviewed
automatically.

## Skills

| Skill | Description |
|-------|-------------|
| `teamsecure` | Orchestrate an adversarial security review (finder → validator → verification) over a PR, a local diff, or a file list |

## Agents

| Agent | Role |
|-------|------|
| `security-paranoid-reviewer` | Aggressive first-pass finder. Builds a coverage inventory, reports every suspicious pattern. Prefers false positives over false negatives. |
| `security-critical-reviewer` | Skeptical validator. Receives findings only (no finder reasoning). Confirms/adjusts/discards each, with a code-traced attack example for MEDIUM+ findings. |

## Usage

```
/teamsecure:teamsecure <PR number | --diff | --files a.go b.go>
```

- `<PR number>` — review a GitHub PR (`gh pr diff`)
- `--diff` — review the local working-tree / uncommitted changes (used by teamimplement)
- `--files ...` — review an explicit list of changed files

### Pipeline

1. Resolve scope and build the authoritative changed-file list
2. **Paranoid pass** — finder produces coverage inventory + findings
3. **Coverage gate** — every non-test backend file must be accounted for, or the finder is re-dispatched
4. **Critical pass** — validator receives findings only, assigns verdicts + severity, builds attack examples for MEDIUM+
5. **Verification** — orchestrator independently re-traces every MEDIUM+ finding (attack-example + precondition reachability + integration boundary)
6. Write the structured findings file

The canonical procedure lives in `skills/teamsecure/references/pipeline.md` and is the
single source of truth that `teamimplement` cites.

## Scope notes

- Mattermost-flavored but portable: rich Mattermost-aware checklist and gov/FedRAMP threat
  framing, no hardcoded per-machine repo paths.
- Output is a structured markdown findings list. No HTML report or chat widget.

## Author

Hassan Mohammed
