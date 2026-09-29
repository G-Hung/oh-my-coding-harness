// Tiny fixture to prove lint, type checking and a behavioral test run together.
export function clamp(value: number, minimum: number, maximum: number): number {
  if (minimum > maximum) throw new RangeError('minimum exceeds maximum');
  return Math.min(maximum, Math.max(minimum, value));
}
