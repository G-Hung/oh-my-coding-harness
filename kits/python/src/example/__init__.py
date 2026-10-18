"""Small fixture for checking the example tooling."""


def unique_names(names: list[str]) -> list[str]:
    """Trim and deduplicate nonempty names while preserving their order."""
    return list(dict.fromkeys(name.strip() for name in names if name.strip()))
