type ResettableChartView = {
  timeScale: () => {
    fitContent: () => void;
  };
  priceScale: (priceScaleId: string) => {
    applyOptions: (options: { autoScale: boolean }) => void;
  };
};

export function resetCandlestickChartView(chart: ResettableChartView | null): boolean {
  if (!chart) return false;
  chart.timeScale().fitContent();
  chart.priceScale("right").applyOptions({ autoScale: true });
  return true;
}
