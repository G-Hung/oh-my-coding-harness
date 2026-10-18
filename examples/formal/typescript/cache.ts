/** Executable protocol example. This class is not a persistent cache adapter. */
export type Load = { key: string; token: number; captured: string; done: boolean };

export class FencedCache {
  authority: Map<string, string>;
  payload = new Map<string, string>();
  tokens = new Map<string, number>();
  pending = new Map<string, Map<number, Load>>();

  constructor(values: Record<string, string>) {
    this.authority = new Map(Object.entries(values));
    for (const key of this.authority.keys()) this.tokens.set(key, 1);
  }

  read(key: string): Load {
    const token = this.tokens.get(key);
    if (token === undefined) throw new Error(`Unknown key: ${key}`);
    const cached = this.payload.get(key);
    if (cached !== undefined) return { key, token, captured: cached, done: true };
    let loads = this.pending.get(key);
    if (!loads) this.pending.set(key, (loads = new Map()));
    let load = loads.get(token);
    if (!load) {
      load = { key, token, captured: this.authority.get(key)!, done: false };
      loads.set(token, load);
    }
    return load;
  }

  invalidate(key: string, value: string, cacheDeleteSucceeds = true): boolean {
    const token = this.tokens.get(key);
    if (token === undefined) throw new Error(`Unknown key: ${key}`);
    this.authority.set(key, value);
    if (!cacheDeleteSucceeds) return false;
    this.payload.delete(key);
    this.tokens.set(key, token + 1);
    return true;
  }

  finish(load: Load): string {
    if (!load.done) {
      // A caller can receive its old snapshot without resurrecting stale cache data.
      if (this.tokens.get(load.key) === load.token) {
        this.payload.set(load.key, load.captured);
      }
      const loads = this.pending.get(load.key);
      loads?.delete(load.token);
      if (loads?.size === 0) this.pending.delete(load.key);
      load.done = true;
    }
    return load.captured;
  }
}
