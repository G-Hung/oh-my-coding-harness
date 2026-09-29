# Inspect preview ports

Copy `check-ports.cjs` into your project's scripts directory. It needs Node.js
and `lsof` (macOS or Linux); no npm packages or application access are needed.
Copy `tests/` too if you want to retain the helper's regression tests.

```sh
node check-ports.cjs --from 3000 --to 3100
node check-ports.cjs --from 4000 --to 4010 --json
node --test tests/*.test.cjs
```

The report contains observed listener ports, PIDs, commands, and the first unused
candidate in the requested range. Exit 1 means inspection failed or all ports
were occupied. Empty successful output from `lsof` means no visible listeners;
permissions may limit visibility.

An unused candidate is not a reservation. Confirm the actual bind and readiness
after launching. Retain the terminal/process handle, stop only a process your
task started, and verify its listener disappears. Never kill an unfamiliar PID
or a process merely because it occupies a desired port.

Separate ports do not isolate build directories or generated files. See the
[verification guide](../../docs/agent-guidelines/verification.md) for ownership
and worktree guidance.
