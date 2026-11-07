import { test } from "node:test";
import assert from "node:assert/strict";
import "../assets/figures.js";

const { TutorFig } = globalThis;

test("rk4 follows xdot = -x", () => {
  const pts = TutorFig.trajectory(s => [-s[0]], [1], 1);
  assert.ok(Math.abs(pts.at(-1)[0] - Math.exp(-1)) < 1e-6);
});

test("trajectory returns T/h + 1 points starting at s0", () => {
  const pts = TutorFig.trajectory(s => [-s[0]], [1], 1);
  assert.equal(pts.length, 101);
  assert.deepEqual(pts[0], [1]);
});

test("pathD draws every point", () => {
  const d = TutorFig.pathD([[0, 0], [1, 2], [2, 1]], x => x * 10, y => y * 10);
  assert.equal(d, "M0.0 0.0L10.0 20.0L20.0 10.0");
});

test("arrowHead is a filled path placed and rotated", () => {
  const s = TutorFig.arrowHead(5, 7, 90);
  assert.match(s, /^<path d="M6 0/);
  assert.match(s, /translate\(5,7\) rotate\(90\)/);
});
