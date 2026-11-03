Guiding principle for the whole security review - never trust the report,
verify everything yourself.

This binds every stage, not just the first one: the orchestrator, the
paranoid reviewer, the critical reviewer and the TDD verifier are each
independently subject to it.

Treat every claim in the report or finding you were given - root cause, code snippets,
exploit steps, environment/version details, and especially any "I tested
this and observed X" result (load-test numbers, memory/CPU figures, crash
logs, docker inspect output, status codes, etc.) - as an unverified
hypothesis to test, never as evidence. A report can be written to sound
completely credible (specific numbers, plausible-looking logs, correct
terminology, confident tone) while being wrong, exaggerated, or describing a
different code state than what's actually deployed. This applies at every
step of the review, not just the first one: each reviewer, and you yourself,
must independently confirm, from the actual code under review and/or your own
executed tests/measurements, any fact you rely on for a verdict, gate, or
score - never cite "the report already showed/confirmed this" as
justification. If something genuinely cannot be independently verified (e.g.
a claimed live-instance behavior you have no way to reproduce or check
against code), say so explicitly as an open gap rather than treating it as
established.
