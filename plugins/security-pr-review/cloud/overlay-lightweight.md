# Lightweight review overlay (low-risk pull requests)

This run is a LIGHTWEIGHT review of a pull request that the pipeline scored as low risk. It uses the same procedure and the same reviewer definitions as a full review, with fewer steps, to spend as few tokens as possible. A finding is reported only when a failing test proves it. The overlay above applies in full, except where this overlay says otherwise: where they conflict, this overlay wins.

## What changes

1. **Mode.** The mode is `lightweight`: use `"mode": "lightweight"` in the structured result.

2. **Step 1.5 (linked context) is skipped.** Write the LINKED CONTEXT section as "skipped (lightweight review)".

3. **Step 2 (paranoid reviewer): one pass only.** Do PASS 1 only: sweep the diff, and read in full only the files that the diff touches. Skip PASS 2 and the mandatory coverage inventory, and skip the coverage validation of Step 2. Keep the candidates that look most likely to be real and rated Medium or higher, strongest first, and verify at most 3 of them (item 8 says what to do when there are more). Do not look at code far from the diff unless a candidate depends on it.

4. **Step 3 (critical reviewer) is skipped.** The failing test of Step 4 is the filter. Rate the severity of each candidate yourself (medium, high or critical), from the real impact of the behavior that its test shows. A candidate that is only Low is dropped.

5. **Step 4 (test-driven verification) is the only filter.**
   - Verify the candidates one at a time, as the verifier definition says, with these limits: at most 2 attempts to get a valid red test and a green test, and no DoS compounding tests (a candidate that can only be shown that way is dropped).
   - A candidate is reported only if the verifier ends with `CONFIRMED_BY_TEST`. Drop every candidate that ends NOT_REPRODUCED, INCONCLUSIVE or TEST_NOT_FEASIBLE: do not report it, with or without a note. This replaces the procedure's reporting of findings that could not be proven. In `notes`, say only how many candidates were dropped for lack of proof.
   - `needs_dynamic` never applies.

6. **Models.** You run on the reasoning model: the paranoid step, the severity and what to report stay with you. The verifier subagent (the one that writes, runs and fixes the tests) runs on `claude-haiku-5-5`: when you launch it, name that model explicitly if your tooling lets you choose one (if the name is rejected, use the closest Haiku 5.5 variant it accepts). If a candidate still has no valid red test after the 2 attempts, make one more attempt for that candidate with the verifier subagent on `claude-sonnet-5-5-medium` (same rule for a rejected name); if that also fails, drop the candidate. If you cannot choose a subagent model, or you run Step 4 yourself, carry on with your own model. In `notes`, say in a few words which model each subagent ran on.

7. **Result.** Use the structured result of the overlay above, with these specifics: `findings` contains only findings whose `verification` is `CONFIRMED_BY_TEST`, each with its `test_ref`; do not use `confidence_note`. An empty `findings` list is a valid result.

8. **More candidates than the limit.** If you found more than 3 candidates, verify only the 3 strongest and never drop the others silently: in `notes`, say how many candidates were left unverified, and set `risk_assessment.agent_level` to `medium` (or `high` if any unverified candidate looks High or Critical). The pipeline treats a raised `agent_level` as the signal to run a full review of the pull request.
