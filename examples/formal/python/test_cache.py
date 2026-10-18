"""Schedule protocol boundaries explicitly instead of sleeping for a race."""

import unittest

from cache import FencedCache


def check_stale_fill(case: unittest.TestCase, cache: FencedCache, old_first: bool) -> None:
    old = cache.read("a")
    case.assertIs(cache.read("a"), old)
    case.assertTrue(cache.invalidate("a", "new"))
    newer = cache.read("a")
    case.assertIsNot(newer, old)
    if old_first:
        case.assertEqual(cache.finish(old), "old")
    case.assertEqual(cache.finish(newer), "new")
    if not old_first:
        case.assertEqual(cache.finish(old), "old")
    case.assertEqual(cache.payload["a"], "new")
    case.assertEqual(cache.finish(cache.read("a")), "new")
    # A second completion must not republish an obsolete result either.
    case.assertEqual(cache.finish(old), "old")
    case.assertEqual(cache.payload["a"], "new")


class CacheConformance(unittest.TestCase):
    def test_old_and_new_completion_orders(self):
        for old_first in (True, False):
            with self.subTest(old_first=old_first):
                check_stale_fill(self, FencedCache({"a": "old"}), old_first)

    def test_invalidation_is_per_key(self):
        cache = FencedCache({"a": "old", "b": "unchanged"})
        a, b = cache.read("a"), cache.read("b")
        cache.invalidate("a", "new")
        self.assertEqual(cache.finish(a), "old")
        self.assertEqual(cache.finish(b), "unchanged")
        self.assertNotIn("a", cache.payload)
        self.assertEqual(cache.payload["b"], "unchanged")

    def test_same_token_loads_join(self):
        cache = FencedCache({"a": "old"})
        first = cache.read("a")
        self.assertIs(cache.read("a"), first)
        self.assertEqual(cache.finish(first), "old")
        self.assertFalse(cache.pending)

    def test_failed_invalidation_does_not_undo_authoritative_write(self):
        cache = FencedCache({"a": "old"})
        cache.finish(cache.read("a"))
        self.assertFalse(cache.invalidate("a", "new", cache_delete_succeeds=False))
        self.assertEqual(cache.authority["a"], "new")
        # Freshness is not guaranteed after failed invalidation.
        self.assertEqual(cache.finish(cache.read("a")), "old")

    def test_contract_rejects_an_unfenced_implementation(self):
        class UnfencedCache(FencedCache):
            def finish(self, load):
                self.payload[load.key] = load.captured
                return load.captured

        with self.assertRaises(AssertionError):
            check_stale_fill(self, UnfencedCache({"a": "old"}), old_first=False)


if __name__ == "__main__":
    unittest.main()
