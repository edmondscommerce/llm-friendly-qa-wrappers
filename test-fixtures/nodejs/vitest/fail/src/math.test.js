import { test, expect } from "vitest";

function add(a, b) {
  return a + b;
}

test("adds 1 + 2 to equal 3", () => {
  expect(add(1, 2)).toBe(3);
});

test("intentionally failing test", () => {
  expect(add(1, 2)).toBe(99);
});
