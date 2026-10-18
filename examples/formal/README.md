# Bounded formal-verification starter

Run a finite TLA+ model and tests against executable Python or TypeScript code.
Use this example to learn the workflow, then replace its contract with one from
your project. This directory works after copying without the rest of the library.

The example checks a cache race: an old load completes after invalidation and a
new read. A token prevents the old load from restoring stale cache data. A second
guard prevents a new request from joining an old pending load. The tests schedule
these steps directly, so they do not depend on a lucky timing window.

## Run it

Use Python 3.10+ and Java 21+. The runner uses only the Python standard library.
The TypeScript example also needs Node 24+. No npm or Python package install is
needed. Node executes the TypeScript sample without type checking it; keep your
project's existing type checker when adopting it.

From this directory, explicitly download the pinned TLC tool once:

```sh
python3 verify.py setup
```

Setup requires network access and verifies the TLC 1.7.2 checksum before saving
the jar. It does not install Java. If a cached jar has the wrong checksum, setup
fails and leaves it unchanged. Inspect that file before removing it or replacing it.

Run either example:

```sh
python3 verify.py --manifest python.json
python3 verify.py --manifest typescript.json
```

Each command runs seven model configurations and five implementation tests.
Both use the same model. To use an existing verified jar, pass
`--tlc-jar path/to/tla2tools-v1.7.2.jar`. Use `--java path/to/java` when Java is
not on PATH. Verification never downloads a missing tool.

Inspect the printed report path. Reports and raw process logs stay under
`.cache/formal/runs/`. Add `--report .cache/formal/latest.json` if you need a
stable report path. A failed or blocked run returns a nonzero exit status.
An explicit report path must end in `.json`. It cannot replace an unrelated file.
TLC may need local socket permission in a restricted execution environment.

The implementation tests also run without Java:

```sh
cd python
python3 -m unittest -v test_cache
```

For TypeScript, run `node --test --test-reporter=tap cache.test.ts` from `typescript/`.
For runner tests, run `python3 -m unittest discover -s tests -v` from this directory.

## What each layer checks

| Configuration | Expected result | Purpose |
| --- | --- | --- |
| `ReadThroughCache.cfg` | Complete exploration, no violation | Check the guarded protocol within its bounds |
| `NoFillFence.cfg` | `NoStaleResurrection` violation | Show that a late old fill requires a token check |
| `NoJoinFence.cfg` | `SameTokenJoin` violation | Show that a pending load must match the current token |
| `BlockedFillWitness.cfg` | `NoBlockedFillWitness` violation | Establish that rejection of an old fill is reachable |
| `SameTokenJoinWitness.cfg` | `NoSameTokenJoinWitness` violation | Establish that same-token coalescing is reachable |
| `IndependentReadWitness.cfg` | `NoIndependentReadWitness` violation | Establish that a new-token request can load independently |
| `FailedInvalidationWitness.cfg` | `NoFailedInvalidationWitness` violation | Establish that an authoritative write can survive failed invalidation |

A negative control removes a guard and must reveal its corresponding defect.
A witness keeps the guards and disproves a deliberately false unreachability
claim. Expected counterexamples are successful checks with different meanings.
Neither a parser error nor a timeout is an expected counterexample.

| Model action | Example implementation | Observable contract |
| --- | --- | --- |
| `Begin` | `read` | Capture the authoritative value and current token on a miss |
| `Join` | Reuse a pending `read` handle | Join only the same key and token |
| `Invalidate` | Successful `invalidate` | Remove payload and rotate the token together |
| `FailedInvalidate` | Failed `invalidate` | Keep the authoritative write without claiming cache freshness |
| `Complete` | `finish` | Return the captured value; publish only under its current token |

The example is an in-memory reference contract. It does not provide a network
cache, locking service, database adapter, or integration-test environment.
The conformance tests assert outcomes independently of implementation guards.
They include both completion orders, two-key isolation, joining, and failed
invalidation. A deliberately unfenced implementation must fail the same contract.

## Copy and adapt

1. Copy this directory, including `verify.py`, `formal_support.py`, the selected
   manifest, model/configuration files, and the selected implementation/tests.
   Keep the other stack only if useful. Preserve `.gitignore` or merge its entries.
2. Identify one protocol and its actual implementation owners. Document its
   invariants, finite bounds, atomic actions, assumptions, and excluded behavior.
3. Adapt the model and configurations. Preserve a baseline and at least one
   guard-removal control. Add witnesses when reachability needs evidence.
4. Replace sample implementations and tests with imports of your actual code.
   Update the manifest paths, commands, and test-summary patterns. The default
   sample passing is evidence about the sample, not your application.
5. Run the adopted command and verify a meaningful failure. Decide explicitly
   whether it belongs in your ship policy. This kit adds no hooks or schedules.

Manifest paths are relative to the manifest directory. Each model declares its
directory, module, checks, and `implementation_files`. Each conformance entry
declares an ID, working directory, argument list, and all relevant input files.
`{python}` means the current interpreter. Commands run without a shell.
Manifests are trusted project configuration: inspect commands before execution.

`tests_pattern` and `skips_pattern` are regular expressions with a named `count`
group. Adapt them to your runner's real summary. A zero count, an unrecognized
summary, or any skipped conformance test fails this check. Keep optional tests
outside this contract instead of silently accepting missing coverage.

The runner hashes the manifest, local model modules/configurations, declared
source/test inputs, runner files, and pinned tool. Declare imported implementation
helpers and relevant configuration too. It cannot discover undeclared dependencies
or certify model-to-code correspondence. Input changes during a run invalidate
the result. Reports identify evidence; they are not reusable proof certificates.

## Bounds, failures, and limits

The model has two keys, two readers, one write per key, and one attempt per reader.
Successful invalidation atomically removes payload and changes token identity.
A failed invalidation can leave stale cache data after the authoritative write.
No freshness claim applies to that failure or to a real system's interval between
its database write and successful cache invalidation.

Terminal states are intentional, so each configuration disables deadlock checking.
No fairness or eventual-completion claim is made. The runner does not disable
deadlock checks globally; other models keep their chosen policy.

The model excludes TTL expiry, arbitrary reader counts, real database isolation,
Redis correctness, authorization, and failures inside its assumed atomic actions.
Real adapters need their own isolated integration tests. The example implementations
do not establish refinement between code and TLA+.

Each configuration has a 60-second timeout. The model phase has a 300-second
budget and a 512 MB Java heap. Each conformance command has a 120-second timeout.
On POSIX systems, timeout and interruption cleanup stops the command's process
group. On other systems, it stops the direct child; the adopted test runner must
clean up any workers or services it starts.
Models run in disposable copies with separate state directories. Logs and reports
remain available after failure. Missing tools or socket permission are BLOCKED;
wrong outcomes, changed inputs, and incomplete exploration are FAILED.

The result applies to the configured finite model and linked tests. It does not
prove the entire application correct. See the
[TLA+ introduction](https://learning.tlapl.us/intro/platform/) for model-checking
scope and the [TLC reference](https://docs.tlapl.us/using:tlc:start) for tool options.
