"""Small executable cache contract; use it as an example, not a storage adapter."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Load:
    key: str
    token: int
    captured: str
    done: bool = False


class FencedCache:
    def __init__(self, values: dict[str, str]):
        self.authority = dict(values)
        self.payload: dict[str, str] = {}
        self.tokens = {key: 1 for key in values}
        self.pending: dict[tuple[str, int], Load] = {}

    def read(self, key: str) -> Load:
        token = self.tokens[key]
        if key in self.payload:
            return Load(key, token, self.payload[key], done=True)
        identity = (key, token)
        if identity not in self.pending:
            self.pending[identity] = Load(key, token, self.authority[key])
        return self.pending[identity]

    def invalidate(self, key: str, value: str, *, cache_delete_succeeds: bool = True) -> bool:
        """An authoritative write can succeed even when cache deletion fails."""
        self.authority[key] = value
        if not cache_delete_succeeds:
            return False
        self.payload.pop(key, None)
        self.tokens[key] += 1
        return True

    def finish(self, load: Load) -> str:
        if not load.done:
            # The old caller may receive its captured value. It cannot publish
            # that value into a cache whose invalidation token has changed.
            if self.tokens[load.key] == load.token:
                self.payload[load.key] = load.captured
            self.pending.pop((load.key, load.token), None)
            load.done = True
        return load.captured
