---
name: review-migration
description: Analyze Mattermost schema migrations against best practices and generate a review report. Pass a migration number/name as argument or omit to auto-detect new migrations.
user-invocable: true
allowed-tools: Read, Glob, Grep, Bash, Write
---

# Review Migration

Analyze a Mattermost schema migration against best practices and produce a filled-out review report.

## Step 1: Find the migration files

If `$ARGUMENTS` is provided, use it to locate the migration:

```
server/channels/db/migrations/postgres/$ARGUMENTS*.up.sql
server/channels/db/migrations/postgres/$ARGUMENTS*.down.sql
```

If `$ARGUMENTS` is empty, auto-detect new or modified migrations:

1. Run `git diff --name-only HEAD` and `git diff --name-only --cached` to find staged/unstaged migration files.
2. Run `git diff --name-only main...HEAD` to find migrations added on the current branch.
3. If nothing is found, ask the user which migration to review.

Read both the `.up.sql` and `.down.sql` files. If the down migration is missing, flag it.

## Step 2: Analyze against best practices

Check every SQL statement against these rules:

### Critical restrictions

| Rule | Details |
|------|---------|
| **No ALTER COLUMN TYPE** | Takes an exclusive lock and rewrites the entire table. The `ALTER TABLE posts ALTER COLUMN props TYPE jsonb` migration took 8+ hours for some customers. If unavoidable, must use a multi-release migration: add new column, backfill via batches + triggers, switch in next ESR, drop old column in subsequent ESR. |
| **CREATE INDEX must use CONCURRENTLY** | Without CONCURRENTLY, index creation takes a SHARE lock blocking all writes for the duration. On large tables this can be minutes to hours. |
| **DROP INDEX must use CONCURRENTLY** | Same reasoning as CREATE INDEX. |
| **No FOREIGN KEY via ALTER TABLE** | Adding FK constraints scans the entire table and takes SHARE ROW EXCLUSIVE lock, blocking DML except SELECTs. Avoid when possible. |
| **No full-table DELETE or UPDATE** | Must process in batches (100-row batches with offset tracking) to avoid extended locks. |
| **`morph:nontransactional` where needed** | Any migration using `CONCURRENTLY` must have `-- morph:nontransactional` as the **first line of the file**. The morph driver checks `strings.HasPrefix(query, "-- morph:nontransactional")` — placing it mid-file causes it to be ignored, and the entire file runs in a transaction, making CONCURRENTLY fail. |
| **Down migration must exist** | Every `.up.sql` must have a corresponding `.down.sql`. |

### Lock types by operation

| Operation | Table Rewrite | Concurrent DML | Lock Type | Notes |
|-----------|---------------|----------------|-----------|-------|
| CREATE INDEX | No | Yes | None (with CONCURRENTLY) | Must use CONCURRENTLY |
| DROP INDEX | No | Yes | None (with CONCURRENTLY) | Must use CONCURRENTLY |
| ADD COLUMN | No | Yes | ACCESS EXCLUSIVE (metadata only) | Returns instantly, metadata-only lock |
| ALTER COLUMN TYPE | **Yes** | **No** | ACCESS EXCLUSIVE | **Strongly avoid** |
| DROP COLUMN | No | Yes | ACCESS EXCLUSIVE (metadata only) | Marks space as unused |
| ADD FK CONSTRAINT | No | Selects only | SHARE ROW EXCLUSIVE | Scans entire table |
| ADD UNIQUE CONSTRAINT | No | Yes | None (if index created concurrently first) | Create index concurrently, then attach |

### Additional checks

- **Unique constraints**: Should be created by first creating an index concurrently, then attaching it: `ALTER TABLE t ADD CONSTRAINT name UNIQUE USING INDEX idx_name;`
- **NULL-to-value conversions**: Prefer `COALESCE` in application code over UPDATE statements.
- **IF NOT EXISTS / IF EXISTS**: DDL should use these guards for idempotency.
- **Nontransactional file splitting**: If a migration needs both transactional statements (ALTER TABLE) and nontransactional statements (CREATE INDEX CONCURRENTLY), they MUST be in separate migration files. A single file cannot be both transactional and nontransactional.

## Step 3: Assess large-dataset testing need

Flag "large-dataset testing recommended" if any DDL statement touches one of these tables, which are known to be large in production Mattermost deployments:

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

## Step 4: Generate the review report

Output the following markdown template, filling in every section based on your analysis. Use checkmarks for passing checks and X marks for failures with explanations.

~~~markdown
# Schema Migration Review: [version] — [description]

## Schema Changes
- [ ] New table(s): ...
- [ ] New column(s): ...
- [ ] New index(es): ...
- [ ] Modified column(s): ...
- [ ] Dropped object(s): ...

## Safety Analysis

| Check | Status | Notes |
|-------|--------|-------|
| No ALTER COLUMN TYPE | pass/FAIL | ... |
| CREATE INDEX uses CONCURRENTLY | pass/FAIL/N/A | ... |
| DROP INDEX uses CONCURRENTLY | pass/FAIL/N/A | ... |
| No FOREIGN KEY via ALTER TABLE | pass/FAIL | ... |
| No full-table DELETE/UPDATE | pass/FAIL | ... |
| morph:nontransactional where needed | pass/FAIL/N/A | ... |
| Down migration exists | pass/FAIL | ... |
| Transactional/nontransactional split correct | pass/FAIL/N/A | ... |

## Backwards Compatibility
- Compatible with previous ESR: Yes/No
- Can previous Mattermost version run with new schema: Yes/No — [explain: e.g. new columns have defaults, old code ignores them]
- Impact if not compatible: ...

## Table Locks & Impact
- Tables affected: ...
- Lock types acquired: ... (e.g., ACCESS EXCLUSIVE metadata-only, none via CONCURRENTLY)
- Impact to concurrent operations: ...

## Zero Downtime
- Possible: Yes/No
- Reason: ...

## Large-Dataset Testing Recommendation
- **Recommended: Yes/No**
- Reason: ... (e.g., "Index creation on `posts` table which typically has 100M+ rows")
- Tables to seed for testing: ...

## Test Results (fill manually if testing recommended)

| DB | Table Size | Row Count | Duration | Instance |
|----|-----------|-----------|----------|----------|
| PostgreSQL | | | | |

## SQL Queries for Pre-Upgrade
Queries admins can run before upgrading to make the actual migration instantaneous:

```sql
-- PostgreSQL
[relevant migration SQL that can be run ahead of time]
```
~~~

## Step 5: Save the report

Ask the user if they'd like to save the report to a file. Suggest the path:
```
server/channels/db/migrations/reviews/<migration-name>.md
```
