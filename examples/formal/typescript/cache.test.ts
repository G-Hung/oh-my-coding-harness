import assert from 'node:assert/strict';
import { test } from 'node:test';
import { FencedCache } from './cache.ts';
import type { Load } from './cache.ts';

function checkStaleFill(cache: FencedCache, oldFirst: boolean) {
  const old = cache.read('a');
  assert.equal(cache.read('a'), old);
  assert.equal(cache.invalidate('a', 'new'), true);
  const newer = cache.read('a');
  assert.notEqual(newer, old);
  if (oldFirst) assert.equal(cache.finish(old), 'old');
  assert.equal(cache.finish(newer), 'new');
  if (!oldFirst) assert.equal(cache.finish(old), 'old');
  assert.equal(cache.payload.get('a'), 'new');
  assert.equal(cache.finish(cache.read('a')), 'new');
  assert.equal(cache.finish(old), 'old');
  assert.equal(cache.payload.get('a'), 'new');
}

test('old and new completion orders preserve the new cache value', () => {
  for (const oldFirst of [true, false]) checkStaleFill(new FencedCache({ a: 'old' }), oldFirst);
});

test('invalidation affects only its key', () => {
  const cache = new FencedCache({ a: 'old', b: 'unchanged' });
  const a = cache.read('a'), b = cache.read('b');
  cache.invalidate('a', 'new');
  assert.equal(cache.finish(a), 'old');
  assert.equal(cache.finish(b), 'unchanged');
  assert.equal(cache.payload.has('a'), false);
  assert.equal(cache.payload.get('b'), 'unchanged');
});

test('same-token loads join and release pending state', () => {
  const cache = new FencedCache({ a: 'old' });
  const first = cache.read('a');
  assert.equal(cache.read('a'), first);
  assert.equal(cache.finish(first), 'old');
  assert.equal(cache.pending.size, 0);
});

test('failed invalidation does not undo the authoritative write', () => {
  const cache = new FencedCache({ a: 'old' });
  cache.finish(cache.read('a'));
  assert.equal(cache.invalidate('a', 'new', false), false);
  assert.equal(cache.authority.get('a'), 'new');
  assert.equal(cache.finish(cache.read('a')), 'old');
});

test('the contract rejects an unfenced implementation', () => {
  class UnfencedCache extends FencedCache {
    finish(load: Load) {
      this.payload.set(load.key, load.captured);
      return load.captured;
    }
  }
  assert.throws(() => checkStaleFill(new UnfencedCache({ a: 'old' }), false), assert.AssertionError);
});
