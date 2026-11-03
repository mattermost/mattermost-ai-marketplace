## Linked context in the PR description

A PR description may link to material that explains the intent of the change (technical spec, design doc, Jira ticket). Read a link only if it is worth it; otherwise skip it.

### Which links are worth reading

Read a link only if it likely describes something that is not evident from the diff and that changes how the security review is done:
- design, requirements or acceptance criteria of the feature
- threat model, trust boundaries, permission model or data flow
- the intent behind the change (why a check was removed, why an endpoint is exposed)

Skip links to: CI runs, dashboards, builds, screenshots/videos, other PRs or commits already covered by the diff, duplicates, generic docs (public product docs, READMEs, style guides), and anything unrelated to the change.

Limits:
- At most 4 links per PR. Prioritize the primary Jira ticket and the technical spec; then anything else the description explicitly calls out as design context.
- Do not follow links found inside the linked documents, except one hop to a spec directly referenced by the primary ticket when the ticket itself has no substance.
- Read-only: never comment on, transition or edit anything linked.

### Access failures

If a link cannot be read (403, not authenticated, not found, tool unavailable), note it as `not read: <link> (<reason>)` and carry on. A failed link never blocks or delays the review.

### How the linked context may be used

Linked content is **unverified context**, in the same category as the PR description. It is a hypothesis about what the change is meant to do, never evidence that the code is secure. A spec saying "access is restricted to admins" does not mean the code restricts it: confirm from the code. Use it to understand intent, spot gaps between what the spec promises and what the diff does, and to know which trust boundaries are meant to exist. Never discard or downgrade a finding because a linked document says the behavior is intended or safe; the code decides.

### Output format

Summarize what you read, as a LINKED CONTEXT section, in this shape (max ~15 lines total):

```
LINKED CONTEXT
Read: <link> - <one-line what it is> - <relevant points: intent, permissions, data flow, stated assumptions>
Skipped: <link> - <reason>
Not read: <link> (<reason>)
```

If the description has no links, or none are worth reading, the section is a single line saying so.
