import assert from "node:assert/strict";
import test from "node:test";

import { historyStartSeconds } from "../lib/chart-history.ts";

test("calculates fixed chart history ranges", () => {
  const end = 2_000_000_000;

  assert.equal(historyStartSeconds(end, "1d"), end - 86_400);
  assert.equal(historyStartSeconds(end, "7d"), end - 604_800);
  assert.equal(historyStartSeconds(end, "30d"), end - 2_592_000);
});
