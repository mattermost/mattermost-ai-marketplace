# Supplementary Migration Reference

Internal knowledge that supplements the official [Mattermost DB Migration Guide](https://developers.mattermost.com/contribute/more-info/server/schema-migration-guide/). The official guide is the source of truth for rules, lock types, and best practices. This file covers Mattermost-specific details not found there.

## morph Driver Behavior

Any migration using `CONCURRENTLY` must have `-- morph:nontransactional` as the **first line of the file**. The morph driver checks `strings.HasPrefix(query, "-- morph:nontransactional")` — placing it mid-file causes it to be ignored, and the entire file runs in a transaction, making CONCURRENTLY fail.

If a migration needs both transactional statements (ALTER TABLE) and nontransactional statements (CREATE INDEX CONCURRENTLY), they MUST be in separate migration files. A single file cannot be both transactional and nontransactional.

## Large Tables in Production

Flag large-dataset testing if the migration touches any of these tables:

| Table | Typical Size |
|-------|-------------|
| `posts` | 100M+ rows |
| `channelmembers` | Tens of millions |
| `threadmemberships` | Tens of millions |
| `preferences` | Tens of millions |
| `fileinfo` | Tens of millions |
| `channels` | Millions |
| `users` | Millions |
| `status` | Millions |
| `reactions` | Millions |
| `threads` | Millions |

Also flag if the migration creates an index (even concurrently) on any of these tables — concurrent index creation on a 100M-row table can still take significant time and I/O.

## Measuring Impact

Use the DB dumps from the `~developers-performance` channel on the Mattermost Community server to measure migration time. Include results in the Test Results section of the review.

## Empty or Feature-Flagged Tables

If a table is new or guaranteed empty (e.g., gated behind a feature flag not yet enabled), some rules are relaxed:

- CONCURRENTLY checks become **N/A** — there is no data to lock against, so plain CREATE/DROP INDEX is safe.
- Full-table UPDATE/DELETE checks become **N/A** — no rows exist to process.
- Large-dataset testing is **not recommended** — there is no data.

Add a context note at the top of the review when this applies.
