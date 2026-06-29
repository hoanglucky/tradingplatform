export const HISTORY_RANGES = [
  { value: "1d", label: "1D", seconds: 24 * 60 * 60 },
  { value: "7d", label: "1W", seconds: 7 * 24 * 60 * 60 },
  { value: "30d", label: "1M", seconds: 30 * 24 * 60 * 60 },
] as const;

export type HistoryRange = (typeof HISTORY_RANGES)[number]["value"];

export function historyStartSeconds(endSeconds: number, range: HistoryRange): number {
  const selected = HISTORY_RANGES.find((item) => item.value === range) ?? HISTORY_RANGES[0];
  return endSeconds - selected.seconds;
}
