# review-migration

Analyze Mattermost schema migrations against best practices and generate a filled-out Developer Schema Migration Review template.

## Skills

### review-migration

Reads `.up.sql` and `.down.sql` migration files, checks every SQL statement against Mattermost's schema migration best practices, determines lock impact and whether large-dataset performance testing is needed, and generates a markdown review report ready to attach to a PR.

```
/review-migration:review-migration <migration-number-or-name>
```

Pass a migration number or name (e.g. `000156_add_foo`) to review a specific migration, or omit the argument to auto-detect new/uncommitted migration files.

## Author

Ben Cooke
