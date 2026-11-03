Read the right tree - never conclude anything from a bare path into a shared
checkout.

Any local checkouts of the Mattermost repositories (for example your clones of them) may be SHARED and can sit at any
commit. Another session may have them on a feature branch, mid-review, or
simply behind `origin/master`. A bare filesystem read (`Read`, `Grep`, `Glob`,
`cat`, or a plain path handed to any tool) returns whatever that working tree
happens to hold right now — which is NOT necessarily `origin/master`, and NOT
necessarily the code under analysis.

This has already produced wrong verdicts: a shared checkout sitting on a commit
that predated the change under review led two agents to state, with full
confidence, that files present on `origin/master` "do not exist", and one of
them to reframe a real finding as a gap in an imaginary partial-fix branch. The
entire result had to be thrown away and redone.

## The rule

- NEVER move `HEAD` in a shared checkout. No `checkout`, `switch`, `pull`,
  `reset`, `stash`. Another session may be reading it this second.
- NEVER read a shared checkout by bare filesystem path to decide what the code
  currently is.
- Read the intended tree instead, in this order of preference:
  1. A pinned worktree path given to you in your task. Its contents are the
     tree you were asked to analyse. Read it with ordinary paths.
  2. `git -C <repo> show origin/master:<path>` for current master.
  3. `git -C <repo> show <sha>:<path>` for a specific commit.
- If a conclusion depends on something NOT existing (a file, a symbol, a
  function), you must confirm the absence against the intended tree before
  stating it:
  `git -C <repo> ls-tree origin/master --name-only -- <path>` or
  `git -C <repo> grep -n '<symbol>' origin/master -- <paths>`.
  "I did not find it" is not the same as "it is not there", and the difference
  has already inverted a verdict.
- When in doubt about what a checkout holds: `git -C <repo> log -1 --oneline HEAD`.

## If you have no Bash tool - fail closed

Some agents run with `Read, Grep, Glob` only and cannot run git at all. If that
is you, you have NO way to tell which commit a shared checkout is parked on, so:

- You MUST be given a pinned worktree path for the code under analysis.
- If your task did not give you one, STOP and ask for it. Do not fall back to
  reading the shared checkout by path and do not infer the tree's state.
- Never report that a file or symbol is absent based on a bare path read. Report
  instead that you could not verify it and say why.

## Reporting

If you had to work around a stale or ambiguous tree, say so explicitly in your
output, naming the path you actually read. A verdict is only as good as the tree
it was derived from, and the reader cannot see which one you used.
