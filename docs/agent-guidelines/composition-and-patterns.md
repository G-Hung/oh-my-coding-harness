# Composition and patterns

Use when behavior varies across implementations or construction becomes complex.
Start with existing code and actual variation. This guide is self-contained.

| Choice | Use when | Avoid when |
| --- | --- | --- |
| Direct function or constructor | One clear operation or implementation is enough | Creation already duplicates consequential setup rules |
| Composition / dependency injection | Behavior needs explicit collaborators or independently replaceable effects | A framework or extra interface adds no useful boundary |
| Strategy | Callers select among real policies with one contract | Flags hide unrelated inputs, outputs, or effects |
| Factory | Selection and construction share setup or lifecycle rules | It only renames a single constructor |
| Registry | Stable keys select implementations or extensions | A small local branch is clearer, or registration order becomes hidden state |
| Adapter | An external API needs translation into the project's contract | It mirrors the external API without isolating anything |

Prefer composition when capabilities vary independently. Use inheritance when
the subtype can honor the base contract and the hierarchy fits the domain.
A pattern name is not evidence that the extra abstraction helps.

## Examples

Pass an existing collaborator explicitly:

```text
sendReport(report, deliver)
    payload = formatReport(report)
    return deliver(payload)
```

The transformation can be tested independently, and delivery failures remain
visible. This does not require a dependency-injection container.

A factory may use a registry when formats genuinely vary:

```text
factories = { "text": makeTextExporter, "json": makeJsonExporter }
createExporter(kind, config)
    factory = factories.lookup(kind)
    if factory is missing: reject unsupported kind
    return factory(config)
```

For dynamic registration, define duplicate-key behavior, registration ownership,
and lifecycle. Prefer explicit startup wiring over import-time side effects.
Keep selection, construction, and cleanup contracts visible. Do not introduce
dynamic plugins when a fixed map meets the requirement.
