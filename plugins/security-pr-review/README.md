# security-pr-review

The prompts of the automated security review of Mattermost pull requests. The review runs unattended in Cursor cloud agents launched by an n8n pipeline; this plugin is where its instructions live, so anyone can improve them by pull request.

The review has two phases, followed by test-driven verification of every Medium or higher finding:

1. **Paranoid reviewer** (`agents/pr-paranoid-reviewer.md`): aggressive first pass that flags anything suspicious, with a mandatory coverage inventory of every changed file.
2. **Critical reviewer** (`agents/pr-critical-reviewer.md`): validates each candidate from the code, drops false positives and Low findings, and writes the detail for the real ones.
3. **TDD verifier** (`agents/pr-finding-verifier-tdd.md` and `prompts/pr-finding-tdd-verification-prompt.md`): proves each Medium+ finding with a red test that fails for the vulnerable reason (plus a green test), or verifies it from the code when a test is not possible.

The orchestration is `skills/review-pr/SKILL.md`.

## How the pipeline uses these files

The pipeline fetches the files from this repository at the start of every review and records the commit it used. A change merged here applies to the next automated review with no other step, and every finding can be traced to the prompt version that produced it.

It builds the prompt from `cloud/entrypoint.md`: every line that is only `@<relative path>` is replaced by the content of that file (resolved relative to the file that contains it, front matter removed, recursively). It adds nothing else and rewrites nothing. The only parts written specifically for the cloud agent are in `cloud/overlay.md`: the run inputs, running unattended, where the worktree lives, the incremental mode and the structured result format.

## Lightweight review

For pull requests scored as low risk the pipeline assembles `cloud/entrypoint-lightweight.md` instead. It uses the same procedure and the same paranoid and verifier definitions, without the critical reviewer, and `cloud/overlay-lightweight.md` limits the work: one pass over the diff, at most 3 candidates, and only findings proven by a failing test are reported. It runs on cheaper models (Sonnet 5.5 to reason, Haiku 5.5 for the mechanical test work).

## Improving the prompts

Anyone can propose changes by pull request:

- **Reviewer behavior and criteria** (what to look for, how to validate, how to prove): edit the files in `agents/`, `prompts/` and `skills/`.
- **Run inputs, incremental mode and result format**: edit `cloud/overlay.md`. The result schema is validated by the pipeline; if you change it, the validator needs the same change.
- Files are imported with `@<relative path>` on a line of their own. Keep that syntax, and do not put it inside code blocks.
- Keep everything in English, and keep the files free of anything specific to one person or machine.
- Add a case to the pipeline's golden set when you fix a miss, so the improvement is measured rather than assumed.

## Layout

```
.claude-plugin/plugin.json
skills/review-pr/SKILL.md        # orchestration of the review
agents/                          # paranoid, critical and TDD verifier subagents
prompts/                         # shared criteria imported by the agents
cloud/entrypoint.md              # what the pipeline assembles (full review)
cloud/overlay.md                 # run inputs and cloud-only behavior
cloud/entrypoint-lightweight.md  # what the pipeline assembles (lightweight review)
cloud/overlay-lightweight.md     # what changes in the lightweight review
```
