import type { Candle } from "@trading-framework/shared";
import { AppShell } from "../../../components/AppShell";
import { CandlestickChart } from "../../../components/CandlestickChart";
import { getDashboardData } from "../../../lib/api";

const MOCK_CANDLES: Candle[] = [
  { timestamp: "2024-06-19T08:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65020, high: 65240, low: 64880, close: 65180, volume: 182 },
  { timestamp: "2024-06-19T09:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65180, high: 65310, low: 65040, close: 65220, volume: 164 },
  { timestamp: "2024-06-19T10:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65220, high: 65280, low: 64920, close: 65010, volume: 231 },
  { timestamp: "2024-06-19T11:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65010, high: 65140, low: 64770, close: 64860, volume: 246 },
  { timestamp: "2024-06-19T12:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 64860, high: 65090, low: 64720, close: 65040, volume: 218 },
  { timestamp: "2024-06-19T13:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65040, high: 65420, low: 64980, close: 65360, volume: 289 },
  { timestamp: "2024-06-19T14:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65360, high: 65510, low: 65210, close: 65420, volume: 203 },
  { timestamp: "2024-06-19T15:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65420, high: 65470, low: 65130, close: 65200, volume: 174 },
  { timestamp: "2024-06-19T16:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65200, high: 65380, low: 65080, close: 65320, volume: 192 },
  { timestamp: "2024-06-19T17:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65320, high: 65640, low: 65270, close: 65590, volume: 277 },
  { timestamp: "2024-06-19T18:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65590, high: 65710, low: 65410, close: 65480, volume: 205 },
  { timestamp: "2024-06-19T19:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65480, high: 65820, low: 65420, close: 65740, volume: 263 },
  { timestamp: "2024-06-19T20:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65740, high: 65910, low: 65620, close: 65860, volume: 196 },
  { timestamp: "2024-06-19T21:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65860, high: 66020, low: 65690, close: 65720, volume: 221 },
  { timestamp: "2024-06-19T22:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65720, high: 65880, low: 65540, close: 65610, volume: 188 },
  { timestamp: "2024-06-19T23:00:00Z", symbol: "BTCUSDT", timeframe: "1h", open: 65610, high: 65940, low: 65570, close: 65890, volume: 254 },
];

export default async function ChartPage() {
  const [health, readiness, safety] = await getDashboardData();

  return (
    <AppShell health={health} readiness={readiness} safety={safety}>
      <main className="chart-page">
        <header className="chart-toolbar">
          <div className="chart-instrument">
            <span className="chart-symbol">BTCUSDT</span>
            <span className="chart-provider">Binance · mock</span>
          </div>
          <div className="chart-timeframes" aria-label="Selected timeframe">
            <span>1m</span>
            <span>15m</span>
            <span className="is-active">1h</span>
            <span>4h</span>
            <span>1d</span>
          </div>
          <div className="chart-quote">
            <span>Last</span>
            <strong>65,890.00</strong>
            <small>+1.34%</small>
          </div>
        </header>

        <section className="chart-workspace" aria-labelledby="chart-heading">
          <div className="chart-heading-row">
            <div>
              <p className="eyebrow">Price chart</p>
              <h2 id="chart-heading">BTC / USDT · 1 hour</h2>
            </div>
            <span className="mock-status">Mock data</span>
          </div>
          <CandlestickChart
            candles={MOCK_CANDLES}
            symbol="BTCUSDT"
            timeframe="1h"
            height={460}
            loading={false}
            error={null}
          />
          <p className="chart-attribution">
            Charts by{" "}
            <a href="https://www.tradingview.com" target="_blank" rel="noreferrer">
              TradingView
            </a>
          </p>
        </section>
      </main>
    </AppShell>
  );
}
