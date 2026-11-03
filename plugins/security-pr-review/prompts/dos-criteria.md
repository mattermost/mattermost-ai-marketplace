Criteria for confirming (or rejecting) a resource-exhaustion/DoS finding, and
for scoring its CVSS Availability impact.

This is the single source of truth for every reviewer that measures or judges a
DoS finding. If a DoS-type finding reaches you, these are the rules that decide
the verdict. Nothing here is optional and nothing here may be
satisfied by inference from reading the code.

## When this applies

Applies whenever the finding's impact story is resource exhaustion/DoS - CPU,
memory, disk, file descriptors, goroutines/threads, DB connections, or any
other shared resource - regardless of the specific CWE (algorithmic
complexity, missing rate limit, unbounded allocation, etc.). Skip silently
for findings with no resource-exhaustion angle (auth bypass, IDOR, XSS,
information disclosure, etc.).

A single request costing more than baseline is NOT by itself proof of a DoS.
It only becomes a real availability threat if that extra cost compounds when
several requests run concurrently, actually saturating the shared resource
for other users, rather than staying capped to what one request/core/thread
already costs. Before rating the impact of the finding, confirm
which of those two this is - and this confirmation
must be an empirical measurement you (or a delegated subagent) actually run
and observe, never an inference from reading the code (e.g. "no lock/rate-
limit was found, so it must compound" is NOT sufficient by itself - the
absence of a serialization point is a reason to expect compounding, not proof
of it) and never a number taken from the report's own claimed load-test/burst
results (docker OOM logs, memory graphs, status-code counts, etc.) - per the
guiding principle above, those are unverified until you reproduce the
compounding yourself:

The question this verification must answer is not whether a single request is
unusually slow, but whether a single actor can compound that cost through
repeated/concurrent requests until it would genuinely exhaust the shared
resource and take the component down (crash it or render it unresponsive) for
other users - not just add latency to their own request. Judge every finding
strictly from your own measurement of whether cost compounds with load, never
against a specific number, threshold, or prior ticket cited by a report or
found elsewhere - a report's claimed bar is exactly the kind of unverified
claim the never-trust-the-report principle tells you to distrust, and every finding
must be judged purely on its own compounding evidence, not another finding's
numbers. You do not need to actually drive the resource to full
exhaustion/OOM/crash to confirm this (that can be impractical, e.g. on a dev
machine with a large amount of RAM) - it is enough to empirically demonstrate
a clear upward compounding trend with increasing load, and you may stop once
that trend is clearly established. But demonstrating that trend is mandatory:
a flat/bounded resource profile under concurrent load does NOT qualify as a
true-positive DoS, no matter how slow or costly a single request is.

## How to measure the compounding

- Use an in-process concurrent test: add a test, in the review worktree (WT),
  that runs N (10-20) goroutines/threads concurrently exercising the exact
  vulnerable code path (the same call the red test already uses), sampling
  real process memory/CPU (e.g. runtime.ReadMemStats peak HeapInuse, not just
  a monotonic allocation-total counter) during the concurrent burst, and
  compares that peak against a single-execution baseline measured the same
  way. It calls the vulnerable function/handler directly, concurrently,
  in-process. Run it more than once to check the signal is consistent, not a
  one-off fluke.
- If the vulnerable operation cannot be invoked directly in a test process
  (e.g. the compounding depends on real OS-level resource contention - file
  descriptors, DB connection pool, disk I/O - that an in-process test
  wouldn't faithfully represent), the finding cannot be proven by test: it is
  TEST_NOT_FEASIBLE with `needs_dynamic`, as the verification prompt says. Do
  not run anything on a live instance.
- Compounds (aggregate resource usage under concurrent load scales up with N,
  clearly beyond a single request's/core's cost - e.g. aggregate CPU% climbs
  into the hundreds/saturates most available cores, or memory grows roughly
  linearly with N): this establishes a compounding trend, but a trend alone
  is NOT yet sufficient to call this a confirmed DoS - see the mandatory
  follow-up check below. Record the before/after numbers (baseline vs
  payload, at minimum: total wall-clock time and peak/avg aggregate resource
  usage) regardless - they belong in the finding's evidence either way, and
  should inform its severity once the follow-up check below is done.

## The mandatory follow-up check

- **Mandatory follow-up once compounding is found: does it actually cap out
  at a limit that still denies service to other users, or does the cap mean
  nobody else is ever really harmed?** A compounding trend that merely climbs
  up to some ceiling (a concurrency semaphore, a connection pool, a worker
  pool, a rate limiter) and then plateaus is NOT by itself proof of a valid
  DoS - everything in this codebase that uses a shared resource has *some*
  ceiling eventually. I need to be 100% certain this is genuine: compounding
  up to a bounded limit that does not succeed in denying service to other
  users is NOT a valid DoS vulnerability, no matter how clean the compounding
  trend looks. Whenever the compounding measurement above reveals a
  cap/plateau (rather than truly unbounded growth), you MUST run one more
  empirical test - never settle this by inference from the cap's size or
  from "no fallback/timeout was found in the code, so it must starve others"
  - before writing this up as a confirmed DoS:
  - Identify whether the capped/saturated resource (the semaphore, pool,
    queue, etc. that caused the plateau) is also needed by OTHER, unrelated
    legitimate requests - not just by repeated attacker access to the same
    poisoned resource/file/endpoint. If the cap only throttles the attacker's
    own repeated access to their own poisoned resource, with no effect on
    anyone else's unrelated requests, this does NOT qualify as a DoS
    affecting other users - say so explicitly and stop here.
  - If it IS shared with other legitimate requests, write a test (same
    worktree and in-process approach as the compounding test above)
    that keeps the shared resource SATURATED under SUSTAINED attacker-driven
    load (not a single instantaneous burst - sustain it for at least long
    enough to observe a steady-state effect, e.g. on the order of a second or
    more of continuous concurrent attacker requests) and, while that
    saturation is ongoing, issues ONE separate, legitimate request that needs
    the same resource. Measure its latency/outcome against its own
    no-load baseline. This is the real test of the DoS claim: does the
    attacker's sustained pressure measurably delay, queue, or fail that
    unrelated legitimate request, or does it sail through unaffected (e.g.
    because of fair queueing, a per-caller budget, a timeout that lets
    legitimate callers skip the wait, or because the plateaued cost is cheap
    enough that queuing behind it is negligible)?
  - Confirmed (the legitimate request is measurably delayed/degraded/denied
    by the sustained saturation): the DoS impact is now genuinely confirmed,
    including which other functionality is denied/degraded (see the
    severity guidance below) - record the concrete before/after
    latency numbers for the legitimate request the same way as the
    compounding numbers.
  - Not confirmed (the legitimate request is unaffected, or only trivially
    slower in a way that doesn't meaningfully deny service): despite the
    earlier compounding trend, this does NOT qualify as a true-positive DoS -
    say so explicitly, the same way a flat/non-compounding profile would be
    rejected above. The underlying cost/inefficiency may still be worth
    noting as a non-blocking hardening observation, but do not score or
    report it as a DoS vulnerability.
- Does NOT compound (aggregate usage under concurrency stays roughly flat vs
  a single request, e.g. because the expensive path is already serialized
  behind a lock/semaphore/queue): this does NOT qualify as a true-positive DoS,
  regardless of how slow or costly a single request is on its own - say so
  explicitly. The underlying inefficiency may still be worth noting (e.g. as a
  non-blocking hardening observation), but do not score or report it as a DoS
  vulnerability on the strength of single-request cost alone.


## Severity

- **Rating the Availability impact (the CVSS Availability value) of a confirmed
  DoS finding:**
  - **Availability: Low** - the default for most confirmed DoS findings. Use
    this whenever the denial/degradation is scoped to a SPECIFIC component or
    subsystem of the server (e.g. only image processing - uploads,
    thumbnails, previews, profile pictures, team icons, emoji - or only some
    other shared subsystem), while the rest of the Mattermost server keeps
    operating normally for unrelated functionality (posting messages,
    authentication, other API calls, etc.). This still applies even when that
    one subsystem is reachable from many different features that all happen
    to share the same underlying resource (e.g. several upload paths sharing
    one decoder semaphore) - "reachable from many features" is still just
    ONE component being denied, not the whole server, so it stays Low.
  - **Availability: High** - reserved for when the vulnerability can actually
    take down or deny the ENTIRE Mattermost server/instance itself (a full
    server crash, or complete unresponsiveness across all functionality, not
    just one subsystem/feature area). Do not use High just because the
    affected subsystem is popular/widely used or the compounding numbers look
    large - the bar is whether the whole server goes down, not how bad the
    numbers are within one subsystem.
  - This determination follows directly from the mandatory follow-up check
    above: if that check confirms the sustained saturation denies/degrades
    other legitimate requests, scope exactly which functionality was shown to
    be affected (the specific subsystem, or genuinely the whole server) and
    score accordingly - don't default to High just because some other request
    was affected without checking whether that request was in the same
    subsystem or truly unrelated server-wide functionality.
