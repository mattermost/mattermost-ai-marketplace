# claude-md-improver

Audit and improve CLAUDE.md files in repositories. Scans for all CLAUDE.md files, evaluates quality against best practices, outputs a quality report with scores, and makes targeted updates with user approval.

## Skills

| Skill | Description |
|-------|-------------|
| `claude-md-improver` | Audit, score, and improve CLAUDE.md files across a codebase |

## Usage

```
/claude-md-improver:claude-md-improver
```

### What It Does

1. **Discovery** — finds all CLAUDE.md, .claude.md, and .claude.local.md files in the repo
2. **Quality Assessment** — scores each file (A-F) on commands, architecture, patterns, conciseness, currency, and actionability
3. **Quality Report** — outputs a detailed report before making any changes
4. **Targeted Updates** — proposes specific additions as diffs, applies only after user approval

### When to Use

- Setting up a new project's CLAUDE.md
- Periodic maintenance of project context files
- After major refactors that may have outdated existing CLAUDE.md content
- Monorepo audits to ensure package-level CLAUDE.md files are consistent

## Author

Nick Misasi
