import { clamp } from './clamp';
test('clamps either boundary and preserves values inside the range', () => {
  expect(clamp(-1, 0, 10)).toBe(0);
  expect(clamp(11, 0, 10)).toBe(10);
  expect(clamp(4, 0, 10)).toBe(4);
});
test('rejects inverted bounds', () => { expect(() => clamp(3, 10, 0)).toThrow(RangeError); });
