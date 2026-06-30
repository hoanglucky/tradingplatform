export type ModuleStatus = {
  name: string;
  role: string;
  status: "scaffolded" | "read_only" | string;
};

export type SafetyStatus = {
  default_trading_mode: "paper" | string;
  live_trading_enabled: boolean;
  exchange_writes_allowed: boolean;
  exchange_adapter_mode: "read_only" | "write_enabled" | string;
};

export type HealthStatus = {
  status: "ok";
  service: string;
  environment: string;
  trading_mode: string;
};

export type DependencyStatus = {
  name: string;
  status: "ok" | "error";
  detail: string | null;
};

export type ReadinessStatus = {
  status: "ready" | "degraded";
  dependencies: DependencyStatus[];
};

export type Candle = {
  symbol: string;
  timeframe: string;
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type MarketSymbol = {
  id: string;
  exchange: string;
  symbol: string;
  base_asset: string;
  quote_asset: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
};

export type WatchlistItem = {
  id: string;
  symbol_id: string;
  exchange: string;
  symbol: string;
  base_asset: string;
  quote_asset: string;
  created_at: string;
};

export type Watchlist = {
  id: string;
  user_id: string;
  name: string;
  items: WatchlistItem[];
};

export type MultiTimeframeWindowCount = 1 | 2 | 4 | 8;
export type MultiTimeframeTimeframe = string;

export type MultiTimeframeWindow = {
  id: string;
  timeframe: MultiTimeframeTimeframe;
  enabled: boolean;
  reviewChecked: boolean;
};

export type MultiTimeframeLayout = {
  symbol: string;
  windowCount: MultiTimeframeWindowCount;
  windows: MultiTimeframeWindow[];
};

export type UserSettings = {
  id: string;
  user_id: string;
  default_symbol: string;
  default_timeframe: "1m" | "5m" | "15m" | "1h" | "4h" | "1d";
  selected_indicators: string[];
  theme: "light" | "dark" | "system";
  timezone: string;
  multi_timeframe_layout: MultiTimeframeLayout | null;
  created_at: string;
  updated_at: string;
};

export type StrategySignal = {
  strategyId: string;
  symbol: string;
  side: "buy" | "sell" | "hold";
  confidence: number;
  generatedAt: string;
};
