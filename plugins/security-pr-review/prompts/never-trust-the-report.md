Guiding principle for the whole vulnerability triage pipeline - never
trust the report, verify everything yourself.

This binds every stage, not just the first one: the orchestrator,
vuln-critic, vuln-reproducer, variant-hunter, mitigation-reviewer and
surgical-gate are each independently subject to it.

Treat every claim in the researcher's report - root cause, code snippets,
exploit steps, environment/version details, and especially any "I tested
this and observed X" result (load-test numbers, memory/CPU figures, crash
logs, docker inspect output, status codes, etc.) - as an unverified
hypothesis to test, never as evidence. A report can be written to sound
completely credible (specific numbers, plausible-looking logs, correct
terminology, confident tone) while being wrong, exaggerated, or describing a
different code state than what's actually deployed. This applies at every
step of this pipeline, not just Step 1: vuln-critic, vuln-reproducer,
variant-hunter, surgical-gate, and you yourself must each independently
confirm, from the actual current code (origin/master) and/or your own
executed tests/measurements, any fact you rely on for a verdict, gate, or
score - never cite "the report already showed/confirmed this" as
justification. If something genuinely cannot be independently verified (e.g.
a claimed live-instance behavior you have no way to reproduce or check
against code), say so explicitly as an open gap rather than treating it as
established.
