# Contributing

Open an issue to discuss a new workflow or a substantial behavior change. Describe
the problem, the intended users, and the checks that can verify the result.
For vulnerabilities, follow the [security policy](SECURITY.md).

## Prepare and check a change

Use the prerequisites and locked installation commands in the
[maintenance guide](docs/maintenance.md#one-time-local-setup). Hook installation
is optional and requires explicit local setup.

Keep changes focused. Use project-neutral examples. Preserve useful conditions,
recovery steps, and existing tooling when you change an adoption procedure.
Follow the [documentation guide](docs/agent-guidelines/documentation.md) for prose.

During iteration, run:

```sh
uv run --frozen --offline --no-sync python tools/check.py --static-only
```

Before opening a pull request, run:

```sh
uv run --frozen --offline --no-sync python tools/check.py
```

Use a Conventional Commit subject when committing. Explain the problem, resulting
behavior, and validation in the pull request. Report unavailable checks explicitly.
CI runs the full gate; CodeQL reports potential security defects separately.

## Preserve adoption boundaries

This library offers assets to select and adapt. Its maintenance workflows do not
activate requirements in another project. Follow the [adoption guide](docs/adoption.md).
Preserve the target's tools and hook manager. Changes to an existing target
AGENTS.md require explicit approval for those additions.

Dependency update pull requests require review and passing checks. A passing
scanner supports only the checks it performs; review what scripts execute and
what copied instructions authorize.
