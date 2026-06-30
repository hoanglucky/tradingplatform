import type { Candle } from "@trading-framework/shared";

export type StructureSwing = {
  index: number;
  timestamp: string;
  price: number;
  type: "SWING_HIGH" | "SWING_LOW";
  confirmed: boolean;
  source: string;
};

export type StructureSegment = {
  start_index: number;
  start_time: string;
  start_price: number;
  end_index: number;
  end_time: string;
  end_price: number;
  source: string;
};

export type StructureOverlay = {
  swings: StructureSwing[];
  segments: StructureSegment[];
  boxes: unknown[];
  markers: unknown[];
  metadata: Record<string, unknown>;
};

const structureBaseUrl =
  process.env.NEXT_PUBLIC_STRUCTURE_ENGINE_BASE_URL ?? "http://localhost:8108";

function isStructureOverlay(value: unknown): value is StructureOverlay {
  if (!value || typeof value !== "object") return false;
  const record = value as Record<string, unknown>;
  return (
    Array.isArray(record.swings) &&
    Array.isArray(record.segments) &&
    Array.isArray(record.boxes) &&
    Array.isArray(record.markers) &&
    !!record.metadata &&
    typeof record.metadata === "object"
  );
}

export async function fetchStructureOverlay(
  symbol: string,
  timeframe: string,
  candles: Candle[],
  signal?: AbortSignal,
): Promise<StructureOverlay> {
  const response = await fetch(`${structureBaseUrl}/structure/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ symbol, timeframe, candles }),
    signal,
  });
  if (!response.ok) {
    throw new Error(`Structure engine returned ${response.status}.`);
  }
  const payload: unknown = await response.json();
  if (!isStructureOverlay(payload)) {
    throw new Error("Structure engine returned an invalid overlay.");
  }
  return payload;
}
