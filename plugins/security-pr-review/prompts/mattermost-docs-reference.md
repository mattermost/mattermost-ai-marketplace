This is a generic supporting resource: use it whenever a concrete question comes up
during the review that the official Mattermost documentation can resolve - not only about a
configuration setting or a specific feature, but about any relevant aspect of the product
(configuration, roles and permissions, security, architecture, terminology, documented
limits, expected behavior of any part of the product, etc.).

All the official documentation now lives in ONE place: the `docs/` directory of the
`mattermost/mattermost` monorepo itself. NEVER use the `mattermost/docs` repository
(archived, no longer maintained - it may hold outdated or removed content) and never
cite it as a source, even if it shows up in a search result or in your memory from another
time. Inside `docs/` there are two subtrees:
- **End-user / admin docs** (what is deployed to docs.mattermost.com):
  `docs/main/` (e.g. `docs/main/administration-guide/...`)
- **Developer docs** (what is deployed to developers.mattermost.com - internal
  architecture, plugins, APIs, development conventions):
  `docs/develop/`
This applies equally if what you are investigating belongs to another repository (e.g.
Playbooks): the documentation of the WHOLE Mattermost ecosystem lives here, under `docs/`
of the monorepo - never in the Playbooks/Boards/etc. repository nor in `mattermost/docs`.

## Step 1: find the page

Navigate `docs/main/<area>/` or `docs/develop/<area>/` (`ls` / `Glob`), or grep the
`docs/` tree of the monorepo, instead of grepping blindly over the whole repository. The
files are `.mdx`.

## Step 2: read the right version

The documentation you consult must always be the one on `origin/master` - never the one on
a feature/fix branch in progress, which may hold changes that are not merged yet. The
checkout your session starts in may be on another branch, so read from `origin/master`
without touching that working tree:
```bash
git fetch origin master
git show origin/master:docs/main/<relative-path>
git show origin/master:docs/develop/<relative-path>
```
If the `fetch` fails (no network, etc.), carry on with the copy you already have and say so
explicitly in your answer - do not treat it as blocking.
