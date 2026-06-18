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

export type Candle = {
  symbol: string;
  timeframe: string;
  openedAt: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
};

export type StrategySignal = {
  strategyId: string;
  symbol: string;
  side: "buy" | "sell" | "hold";
  confidence: number;
  generatedAt: string;
};

