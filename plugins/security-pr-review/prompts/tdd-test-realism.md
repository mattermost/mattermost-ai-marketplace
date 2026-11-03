**Actor privilege level matters as much as the input.** Perform the attacker
action in the red test using a test client/fixture whose role/permissions
match exactly what the finding claims the attacker has — e.g.
Go's `th.Client` (a plain team member) rather than `th.SystemAdminClient` or
`th.LocalClient`, unless the finding is specifically about a sysadmin-only
boundary. Always use the lowest privilege level that still reproduces the
bypass: an elevated actor often has the permission
being tested anyway, or bypasses the check entirely, so a red test built
around one can pass "for the wrong reason" and prove nothing about the
actual authorization gap. If the test needs a second user for setup (e.g. a
victim, or an object the attacker's request references), give that second
user only the role the scenario actually requires too — do not default to
sysadmin for either party purely for convenience.
