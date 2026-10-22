# Security policy

## Supported code

Security fixes target the latest revision of the default branch. Older copied
assets and modified copies do not receive automatic updates. Compare your copy
with the current library and adapt applicable fixes to your project.

## Report a vulnerability

Do not put credentials, exploit details, or private project data in public issues
or pull requests. Use GitHub's **Report a vulnerability** option in this
repository's **Security** tab when private vulnerability reporting is enabled.

If that option is unavailable, open an issue asking the maintainer to enable
private reporting. Include no vulnerability details. Wait for a private reporting
channel before sharing the report. This policy does not promise a response time.

In the private report, include the affected revision or asset, prerequisites,
reproduction steps, and expected impact. Use a minimal example without live
credentials or private data. If a credential was exposed, revoke or rotate it;
deleting the file does not invalidate the credential.

## Security checks and limits

CI checks the library's maintained behavior. CodeQL scans Python and
JavaScript/TypeScript. Dependabot proposes dependency updates. GitHub secret
scanning and push protection require repository settings; workflow files do not
enable them. See the [activation checklist](docs/maintenance.md#github-security-activation).

These checks can miss defects, unsupported secret patterns, and unsafe uses of
copied assets. Review script execution, permissions, and agent instructions in
the target project's context before adoption.
