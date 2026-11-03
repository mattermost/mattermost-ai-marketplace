# security-pr-review

Two-phase security review of a Mattermost pull request, followed by test-driven verification of every Medium or higher finding:

1. **Paranoid reviewer** (`agents/pr-paranoid-reviewer.md`): aggressive first pass that flags anything suspicious, with a mandatory coverage inventory of every changed file.
2. **Critical reviewer** (`agents/pr-critical-reviewer.md`): validates each candidate from the code, drops false positives and Low findings, and writes the detail for the real ones.
3. **TDD verifier** (`agents/pr-finding-verifier-tdd.md` and `prompts/pr-finding-tdd-verification-prompt.md`): proves each Medium+ finding with a red test that fails for the vulnerable reason (plus a green test), or verifies it from the code when a test is not possible.

The orchestration is `skills/review-pr/SKILL.md`.

## Use locally

```
/plugin install security-pr-review@mattermost-ai-marketplace
/security-pr-review:review-pr <PR number>
```

Run it from a clone of `mattermost/mattermost`. It creates an isolated worktree for the PR and never moves your `HEAD`. Nothing is posted on GitHub: you get the findings and the comment drafts.

## Use in the automated cloud review agents

The automated pipeline (n8n launching Cursor cloud agents) runs these exact files. It fetches them from this repository at the start of every review and records the commit it used, so a change merged here applies to the next automated review with no other step, and every finding can be traced to the prompt version that produced it.

How the pipeline builds the prompt: it starts at `cloud/entrypoint.md` and replaces every line that is only `@<relative path>` with the content of that file (resolved relative to the file that contains it, front matter removed, recursively). It adds nothing else and rewrites nothing. The only parts written for the cloud are in `cloud/overlay.md`: the differences of running unattended in a Cursor cloud agent (no human to ask, where the worktree lives, nothing written to GitHub, the structured result format). Keep that file as small as possible.

## Improving the prompts

Anyone can propose changes by pull request:

- **Reviewer behavior and criteria** (what to look for, how to validate, how to prove): edit the agent and prompt files. These are shared by local and cloud runs, so write them so they work in both: no personal paths, no assumptions about one machine. If you need something that is true only in the cloud, put it in `cloud/overlay.md` instead.
- **Cloud-only behavior and the result format**: edit `cloud/overlay.md`. The result schema is validated by the pipeline; if you change it, the validator needs the same change.
- Files are imported with `@<relative path>` on a line of their own. Keep that syntax, and do not put it inside code blocks.
- Add a test case to the pipeline's golden set when you fix a miss, so the improvement is measured rather than assumed.

## Layout

```
.claude-plugin/plugin.json
skills/review-pr/SKILL.md        # orchestration (the /review-pr command)
agents/                          # paranoid, critical and TDD verifier subagents
prompts/                         # shared criteria imported by the agents
cloud/entrypoint.md              # what the automated pipeline assembles
cloud/overlay.md                 # cloud-only differences
```
