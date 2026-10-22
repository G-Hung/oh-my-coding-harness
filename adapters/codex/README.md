# Codex adoption notes

The repository provides [ship-cycle](../../.agents/skills/ship-cycle/SKILL.md)
and [code-sweep](../../.agents/skills/code-sweep/SKILL.md). Each skill contains its
workflow. Copy selected skills into the host's supported skill location.

Use existing host settings by default. Model preferences are optional and must
match available capabilities. No project file automatically changes a running
agent's model or supplies independent-review capability.

In Codex, invoke `$ship-cycle execute` for approved implementation or
`$code-sweep` for a read-only review. Switch from planning to execution when
implementing. In other hosts, use their equivalent invocation and agent tools.

A fresh reviewer means a separate review context, not a provider-specific
argument or a different model. Keep that reviewer through repairs and explicit
approval. See the [adoption guide](../../docs/adoption.md) for integration.
