"use client";

import type { Candle } from "@trading-framework/shared";
import { useEffect, useRef } from "react";
import {
  CandlestickSeries,
  ColorType,
  createChart,
  type CandlestickData,
  type IChartApi,
  type ISeriesApi,
  type Time,
  type UTCTimestamp,
} from "lightweight-charts";
import { resetCandlestickChartView } from "../lib/chart-view";
import { candleOpenTimestampSeconds, formatChartTime } from "../lib/chart-time";

export type CandlestickChartProps = {
  candles: Candle[];
  symbol: string;
  timeframe: string;
  timezone: string;
  height: number;
  loading: boolean;
  error: string | null;
};

function toChartData(candles: Candle[]): CandlestickData<UTCTimestamp>[] {
  return candles
    .map((candle) => ({
      time: candleOpenTimestampSeconds(candle.timestamp) as UTCTimestamp,
      open: candle.open,
      high: candle.high,
      low: candle.low,
      close: candle.close,
    }))
    .filter((candle) => Number.isFinite(candle.time))
    .sort((left, right) => Number(left.time) - Number(right.time));
}

export function CandlestickChart({
  candles,
  symbol,
  timeframe,
  timezone,
  height,
  loading,
  error,
}: CandlestickChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const fitContentRef = useRef(false);
  const chartHeight = Math.max(height, 240);
  const hasData = candles.length > 0;

  useEffect(() => {
    const container = containerRef.current;
    if (!container || loading || error || !hasData) {
      return;
    }

    const chart = createChart(container, {
      width: container.clientWidth,
      height: chartHeight,
      layout: {
        background: { type: ColorType.Solid, color: "#ffffff" },
        textColor: "#5e6b78",
        attributionLogo: false,
      },
      localization: {
        timeFormatter: (time: Time) => formatChartTime(time, timezone, "crosshair"),
      },
      grid: {
        vertLines: { color: "#eef1f4" },
        horzLines: { color: "#eef1f4" },
      },
      rightPriceScale: {
        borderColor: "#d8dee6",
      },
      timeScale: {
        borderColor: "#d8dee6",
        timeVisible: true,
        secondsVisible: timeframe === "1m",
        tickMarkFormatter: (time: Time) => formatChartTime(time, timezone, "axis"),
      },
      crosshair: {
        vertLine: { color: "#718096", labelBackgroundColor: "#17202a" },
        horzLine: { color: "#718096", labelBackgroundColor: "#17202a" },
      },
    });

    const series = chart.addSeries(CandlestickSeries, {
      upColor: "#0d9488",
      downColor: "#dc4c3f",
      borderVisible: false,
      wickUpColor: "#0d9488",
      wickDownColor: "#dc4c3f",
    });
    chartRef.current = chart;
    seriesRef.current = series;
    fitContentRef.current = true;

    const resizeObserver = new ResizeObserver(([entry]) => {
      chart.applyOptions({ width: Math.floor(entry.contentRect.width) });
    });
    resizeObserver.observe(container);

    return () => {
      chartRef.current = null;
      seriesRef.current = null;
      fitContentRef.current = false;
      resizeObserver.disconnect();
      chart.remove();
    };
  }, [chartHeight, error, hasData, loading, timeframe, timezone]);

  useEffect(() => {
    if (!loading && !error && seriesRef.current) {
      seriesRef.current.setData(toChartData(candles));
      if (fitContentRef.current) {
        chartRef.current?.timeScale().fitContent();
        fitContentRef.current = false;
      }
    }
  }, [candles, error, loading, timeframe]);

  if (loading) {
    return (
      <div className="chart-state" style={{ height: chartHeight }} role="status">
        <span className="chart-spinner" aria-hidden="true" />
        <strong>Loading {symbol}</strong>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-state chart-state-error" style={{ height: chartHeight }} role="alert">
        <strong>Chart unavailable</strong>
        <span>{error}</span>
      </div>
    );
  }

  if (candles.length === 0) {
    return (
      <div className="chart-state" style={{ height: chartHeight }}>
        <strong>No candles</strong>
        <span>
          {symbol} · {timeframe}
        </span>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      className="chart-canvas"
      style={{ height: chartHeight, minHeight: chartHeight }}
      aria-label={`${symbol} ${timeframe} candlestick chart`}
      onContextMenu={(event) => {
        event.preventDefault();
        resetCandlestickChartView(chartRef.current);
      }}
    />
  );
}
