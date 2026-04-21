# AI-Powered Development Process

Source: [PE: AI-Powered Development Process](https://mattermost.atlassian.net/wiki/spaces/pde/pages/4364763143/AI-Powered+Development+Process)

These principles govern how longshot operates and what quality bar it targets.

## Design

New capabilities that are more than ~2 weeks of development time should generally have four artifacts:

1. **PRFAQ** — starts from the end to describe the value to the customer and the scope of requirements
2. **UX Spec** — describes the user-facing behavior and interaction patterns
3. **Technical Spec** — describes the implementation approach; must be complete and linked before development begins
4. **Jira Epic** — a focused epic containing all stories required to ship the capability with clear target start and end dates (see [Jira Epic Guidelines](https://mattermost.atlassian.net/wiki/spaces/pde/pages/4364763143/AI-Powered+Development+Process))

For fundamental architectural or technical debt work, PRFAQ or UX Spec may not be needed. Use your best judgement.

Each artifact should be reviewed with relevant stakeholders in a kick-off call and have a dedicated Mattermost channel for collaboration.

## Development

Once specs are in place and development begins:

- **Feature flags** — all new capabilities must be behind a feature flag by default. This allows merging smaller PRs before the full feature is complete and provides an escape valve if instability is discovered after release. See [Feature Flags Guidelines](https://mattermost.atlassian.net/wiki/spaces/pde/pages/4364763143/AI-Powered+Development+Process).
- **AGENTS.md** — use the repository's AGENTS.md to provide AI tools with shared context. Keep it intentional and treat workarounds as technical debt to address. Follow the [guidelines for updating AGENTS.md](https://mattermost.atlassian.net/wiki/spaces/pde/pages/4364763143/AI-Powered+Development+Process).
- **Token usage** — AI should be your primary driver for implementation and should be used extensively, but avoid being careless. See [Token Optimization](https://mattermost.atlassian.net/wiki/spaces/pde/pages/4364763143/AI-Powered+Development+Process) for lightweight guidance.

## Submitting PRs

A PR is a point of pride. Reviewers are not a safety net. Respect your colleagues' time and enable fast iteration through submitting great PRs:

- **Self-review first** — before requesting review, read through your own PR as if seeing it for the first time. Look for anything that would confuse a reviewer.
- **Automated tests are required** — unit, E2E, and other applicable automated tests must be included in the same PR — not submitted as a follow-up after merge. PRs without tests will not be merged unless a clear, valid reason is documented.
- **AI review before human review** — run one or more AI code reviews (e.g. CodeRabbit) to catch issues before a human sees the PR.
- **Strong description** — state the problem in your own words, summarize the approach, and include any relevant AI plan or context used during development. Point reviewers toward the tricky parts.
- **Highlight areas for human review** — particularly for larger PRs, call out the changes that you would like reviewers to scrutinize the most.
- **Keep it scoped** — fix the problem at hand. Avoid unrelated changes in the same PR, no matter how tempting.
- **Keep PRs small where possible** — prefer many small PRs over a single large one. Each PR should have a clear, singular purpose. If a change is large, use AI to split into smaller, logical commits and PRs.
- **Rebase before submitting** — rebase on the target branch before opening the PR. Avoid force-pushing after a review has started — it hides the history of changes from reviewers.

## Reviewing PRs

Reviews should be timely, constructive, and focused on what matters:

- **One required human reviewer** — a single product engineer code review is required before merge. The PR submitter is accountable for the quality of the work — not the reviewer.
- **Submitter decides on additional reviews** — the PR submitter is responsible for determining whether QA, security, or UX review is needed, and for requesting it.
- **Merged = ready to ship** — unless a feature flag is intentionally keeping it off, code merged to the main branch should be considered production-ready. Do not merge work that is not ready to be shipped.
- **Acknowledge review requests within 2 business days** — if you are requested as a reviewer and cannot make the time, decline the request. Do not leave PRs waiting.
- **Once reviewing a PR, don't leave it hanging** — give it the attention it deserves and actively engage with the submitter through comments, channels, or on a call to unblock them.
- **Focus on high impact feedback** — the primary value of the review is to identify and deliberate on fundamental software design issues. Leave code style and nitpicks to linters and AI review.

## Verifying Tickets

Engineers own the full lifecycle of their work — through to verification that it is working as expected in a real environment:

- **Drink our own champagne** — ensure new capabilities are tested on internal servers like community or hub before considering the work done. "It works locally" is not sufficient.
- **Enlist support when needed** — engineers can and should request help from QA, PM, or others for verification — but they remain accountable for verifying the success of the change.
- **Engineers close their own tickets** — once verification that the merged changes is complete (fix or change working as expected on community/hub) then engineers close the ticket. In cases where it's not possible to verify on community/hub, set up another environment to do verification.
- **Close the loop** — all new capabilities must have a lighthouse customer. Follow-up with the CSM/TAM for that customer so they can demo the changes and close the loop with the customer.
