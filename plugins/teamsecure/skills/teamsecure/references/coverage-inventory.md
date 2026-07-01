# Coverage inventory specification

The paranoid finder's output MUST begin with a coverage inventory table before any
findings. The orchestrator's coverage gate (pipeline Step 3) validates it. Its purpose is
to make "what was reviewed" explicit and auditable: an unmentioned file is treated as NOT
reviewed.

## Table format

| File | Category | Status |
|------|----------|--------|
| api/api_post.go | backend-go | reviewed-with-findings [F-001] |
| server/channels/app/user.go | backend-go | reviewed-no-findings |
| conversations/handle_messages.go | backend-other | reviewed-no-findings |
| webapp/src/components/question_card.tsx | webapp | reviewed-no-findings |
| config/default.json | config/other | reviewed-no-findings |
| mmtools/ask_user_question_test.go | test | omitted (test) |

## Categories
- `backend-go` — Go server/plugin code (may live at the repo root, not only under `server/`).
- `backend-other` — non-Go backend code (e.g. Python, Node services).
- `webapp` — frontend (React/TypeScript) code.
- `test` — test-only files.
- `config/other` — configuration, infra, docs, build files.

## Test-file patterns (omittable)

A file is a `test` file (omittable per rule 4 below) when it matches any of these — do NOT let
an unfamiliar test-naming convention trigger a false gate failure:

- `*.test.*`, `*.spec.*`
- `*.e2e.*` (end-to-end, e.g. detox/cypress)
- `*.benchmark.*`
- `*.cl.*` (component-library / story files)
- `__snapshots__/` and `*.snap`
- `test_fixtures*`, `*_fixtures.*`, `**/fixtures/**`
- anything under a clearly test-only directory: `**/e2e/**`, `**/__tests__/**`, `**/__mocks__/**`

When a match is ambiguous (a file that is test-adjacent but contains real logic), review it
rather than omit it. Test *support/helper* files that ship secrets or bind a server to a
non-loopback host are still worth a finding even though they are "tests".

## Gate rules (enforced by the orchestrator)
1. **File-count match:** the number of rows equals the number of files in the authoritative
   changed-file list. If it does not match, coverage is incomplete — re-dispatch the finder.
2. **No silent omissions of backend files:** every `backend-go` and `backend-other` file
   must end as `reviewed-no-findings` or `reviewed-with-findings [IDs]`. Never "omitted".
3. **Webapp files** are reviewed in the full sweep; they may end as `reviewed-no-findings`.
4. **Test files** (matching the patterns above) may be `omitted (test)` UNLESS the diff
   removes or weakens security tests — then it is a finding, and the row should be
   `reviewed-with-findings [IDs]`.
5. **Silence is not coverage.** A file absent from the table is a review failure; re-dispatch.

The orchestrator does not advance to the critical pass (or to Step 3.5 reconcile) until the
gate passes.
