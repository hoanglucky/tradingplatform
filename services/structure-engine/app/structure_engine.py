"""
TLP Swing Chart - PineScript to Python conversion for structure-engine.

Source behavior converted from the uploaded TradingView PineScript indicator:
- TLP swing line logic
- Inside/outside bar detection
- Inside-bar consolidation boxes
- NoS / NoD markers

Important:
This module does not draw on a chart. It returns structured overlay data that the
frontend can render with TradingView Lightweight Charts or another chart library.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Iterable, Literal, Optional

SwingType = Literal["SWING_HIGH", "SWING_LOW"]
MarkerType = Literal["INSIDE_BAR", "OUTSIDE_BAR", "NO_S", "NO_D", "SWING_HIGH", "SWING_LOW"]


@dataclass(frozen=True)
class Candle:
    """Normalized OHLCV candle input used by structure-engine."""

    timestamp: Any
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


@dataclass
class TLPConfig:
    """Runtime config equivalent to the PineScript indicator inputs."""

    show_tlp: bool = True
    show_inside_bars: bool = False  # Pine input sib default false
    show_outside_bars: bool = True  # Pine input sob default true
    detect_inside_bar_zones: bool = True
    include_swing_markers: bool = True


@dataclass
class SwingPoint:
    index: int
    timestamp: Any
    price: float
    type: SwingType
    confirmed: bool = True
    source: str = "tlp_pine_converted"


@dataclass
class SwingSegment:
    start_index: int
    start_time: Any
    start_price: float
    end_index: int
    end_time: Any
    end_price: float
    source: str = "tlp_pine_converted"


@dataclass
class StructureBox:
    start_index: int
    end_index: int
    price_high: float
    price_low: float
    type: str = "INSIDE_BAR_ZONE"
    source: str = "tlp_pine_converted"


@dataclass
class StructureMarker:
    index: int
    timestamp: Any
    price: float
    type: MarkerType
    location: Literal["abovebar", "belowbar", "onbar"]
    source: str = "tlp_pine_converted"


@dataclass
class TLPStructureResult:
    swings: list[SwingPoint]
    segments: list[SwingSegment]
    boxes: list[StructureBox]
    markers: list[StructureMarker]
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "swings": [asdict(item) for item in self.swings],
            "segments": [asdict(item) for item in self.segments],
            "boxes": [asdict(item) for item in self.boxes],
            "markers": [asdict(item) for item in self.markers],
            "metadata": self.metadata,
        }


class TLPSwingAnalyzer:
    """
    Python implementation of the uploaded TLP Swing PineScript.

    The PineScript uses persistent arrays and TradingView line/box/plotshape
    drawing calls. This Python port keeps the same core state transitions but
    returns data structures instead of chart objects.
    """

    def __init__(self, config: Optional[TLPConfig] = None) -> None:
        self.config = config or TLPConfig()

    @staticmethod
    def _normalize_candles(candles: Iterable[Candle | dict[str, Any]]) -> list[Candle]:
        normalized: list[Candle] = []
        for item in candles:
            if isinstance(item, Candle):
                normalized.append(item)
            else:
                normalized.append(
                    Candle(
                        timestamp=item.get("timestamp", item.get("time")),
                        open=float(item["open"]),
                        high=float(item["high"]),
                        low=float(item["low"]),
                        close=float(item["close"]),
                        volume=float(item.get("volume", 0.0)),
                    )
                )
        return normalized

    @staticmethod
    def _stronger_point(point_type: SwingType, a: SwingPoint, b: SwingPoint) -> SwingPoint:
        if point_type == "SWING_HIGH":
            return b if b.price >= a.price else a
        return b if b.price <= a.price else a

    def analyze(self, candles: Iterable[Candle | dict[str, Any]]) -> TLPStructureResult:
        data = self._normalize_candles(candles)
        if not data:
            return TLPStructureResult(
                swings=[],
                segments=[],
                boxes=[],
                markers=[],
                metadata={"source": "tlp_pine_converted", "bars": 0},
            )

        boxes: list[StructureBox] = []
        markers: list[StructureMarker] = []
        swing_points: list[SwingPoint] = []

        # Pine: var aCZ = array.new_float(0)
        consolidation_zone_values: list[float] = []

        first = data[0]
        initial_range = abs(first.high - first.low)

        # Pine arrays:
        # var arrayX = array.new_int(5, bar_index)
        # var arrayY = array.new_float(); then pushes 5 initial values.
        array_x = [0, 0, 0, 0, 0]
        array_y = [
            first.close - initial_range * 1,
            first.close + initial_range * 1,
            first.close - initial_range * 2,
            first.close + initial_range * 2,
            first.close,
        ]

        # The PineScript carries highPrev/lowPrev forward through inside bars.
        prev_effective_high = first.high
        prev_effective_low = first.low

        def register_swing(index: int, price: float, point_type: SwingType) -> None:
            point = SwingPoint(
                index=index,
                timestamp=data[index].timestamp,
                price=price,
                type=point_type,
            )
            if swing_points and swing_points[-1].type == point_type:
                swing_points[-1] = self._stronger_point(point_type, swing_points[-1], point)
            else:
                swing_points.append(point)

        def pop_push(index: int, price: float, point_type: SwingType) -> None:
            # Pine: array.pop(_array); array.push(_array, _value)
            array_x.pop()
            array_y.pop()
            array_x.append(index)
            array_y.append(price)
            register_swing(index, price, point_type)

        def shift_push(index: int, price: float, point_type: SwingType) -> None:
            # Pine: array.shift(_array); array.push(_array, _value)
            array_x.pop(0)
            array_y.pop(0)
            array_x.append(index)
            array_y.append(price)
            register_swing(index, price, point_type)

        for i, candle in enumerate(data):
            prev = data[i - 1] if i > 0 else None

            # Inside/outside/noS/noD markers from the bottom PineScript section.
            if prev is not None:
                if self.config.show_inside_bars and candle.high <= prev.high and candle.low >= prev.low:
                    markers.append(
                        StructureMarker(
                            index=i,
                            timestamp=candle.timestamp,
                            price=candle.close,
                            type="INSIDE_BAR",
                            location="onbar",
                        )
                    )

                if self.config.show_outside_bars and candle.high > prev.high and candle.low < prev.low:
                    markers.append(
                        StructureMarker(
                            index=i,
                            timestamp=candle.timestamp,
                            price=candle.close,
                            type="OUTSIDE_BAR",
                            location="onbar",
                        )
                    )

                no_s = prev.close < prev.open and candle.close > candle.open and candle.low < prev.low
                no_d = prev.close > prev.open and candle.close < candle.open and candle.high > prev.high

                if no_s:
                    markers.append(
                        StructureMarker(
                            index=i,
                            timestamp=candle.timestamp,
                            price=candle.low,
                            type="NO_S",
                            location="belowbar",
                        )
                    )
                if no_d:
                    markers.append(
                        StructureMarker(
                            index=i,
                            timestamp=candle.timestamp,
                            price=candle.high,
                            type="NO_D",
                            location="abovebar",
                        )
                    )

            # Inside-bar consolidation zone logic.
            if self.config.detect_inside_bar_zones and prev is not None:
                highest = prev.high
                lowest = prev.low
                if len(consolidation_zone_values) > 0:
                    highest = consolidation_zone_values[0]
                    lowest = consolidation_zone_values[1]

                inside_bar_condition = (
                    candle.low >= lowest
                    and candle.low <= highest
                    and candle.high >= lowest
                    and candle.high <= highest
                )

                if inside_bar_condition:
                    # Pine pushes previous high/low, not current high/low.
                    consolidation_zone_values.append(prev.high)
                    consolidation_zone_values.append(prev.low)

                if len(consolidation_zone_values) >= 2 and not inside_bar_condition:
                    bar_count = len(consolidation_zone_values) // 2
                    boxes.append(
                        StructureBox(
                            start_index=max(0, i - bar_count - 1),
                            end_index=i - 1,
                            price_high=max(consolidation_zone_values),
                            price_low=min(consolidation_zone_values),
                        )
                    )
                    consolidation_zone_values.clear()

            if i == 0:
                continue

            # Main TLP swing state machine.
            # Pine comment:
            # 0: Continue, 1: Reversal, Outside bar 2: Continue, 3: Continue and reversal.
            draw_line = 0
            current_effective_high = candle.high
            current_effective_low = candle.low

            if candle.high > prev_effective_high and candle.low > prev_effective_low:
                # Higher high + higher low.
                if array_y[4] >= array_y[3]:
                    if candle.high > array_y[4]:
                        pop_push(i, candle.high, "SWING_HIGH")
                else:
                    shift_push(i, candle.high, "SWING_HIGH")
                    draw_line = 1

            elif candle.high < prev_effective_high and candle.low < prev_effective_low:
                # Lower high + lower low.
                if array_y[4] >= array_y[3]:
                    shift_push(i, candle.low, "SWING_LOW")
                    draw_line = 1
                else:
                    if candle.low < array_y[4]:
                        pop_push(i, candle.low, "SWING_LOW")

            elif candle.high >= prev_effective_high and candle.low <= prev_effective_low:
                # Outside bar.
                if array_y[4] > array_y[3]:
                    if candle.high > array_y[4]:
                        pop_push(i, candle.high, "SWING_HIGH")
                        draw_line = 2
                    if array_y[3] > candle.low:
                        shift_push(i, candle.low, "SWING_LOW")
                        draw_line = 3
                elif array_y[4] < array_y[3]:
                    if candle.low < array_y[4]:
                        pop_push(i, candle.low, "SWING_LOW")
                        draw_line = 2
                    if candle.high > array_y[3]:
                        shift_push(i, candle.high, "SWING_HIGH")
                        draw_line = 3

            elif candle.high <= prev_effective_high and candle.low >= prev_effective_low:
                # Inside bar: keep previous effective high/low.
                current_effective_high = prev_effective_high
                current_effective_low = prev_effective_low

            # Keep these values for the next bar, matching highPrev/lowPrev series behavior.
            prev_effective_high = current_effective_high
            prev_effective_low = current_effective_low

            # draw_line is included in metadata-style marker only through final segments.
            _ = draw_line

        if self.config.include_swing_markers:
            for point in swing_points:
                markers.append(
                    StructureMarker(
                        index=point.index,
                        timestamp=point.timestamp,
                        price=point.price,
                        type=point.type,
                        location="abovebar" if point.type == "SWING_HIGH" else "belowbar",
                    )
                )

        segments = [
            SwingSegment(
                start_index=a.index,
                start_time=a.timestamp,
                start_price=a.price,
                end_index=b.index,
                end_time=b.timestamp,
                end_price=b.price,
            )
            for a, b in zip(swing_points, swing_points[1:])
            if a.index != b.index or a.price != b.price
        ]

        return TLPStructureResult(
            swings=swing_points,
            segments=segments,
            boxes=boxes,
            markers=markers,
            metadata={
                "source": "tlp_pine_converted",
                "original_indicator": "TLP Swing Chart",
                "bars": len(data),
                "notes": [
                    "PineScript drawing calls were converted into structured overlay data.",
                    "TLP lines are returned as swing segments.",
                    "Inside-bar boxes are returned as StructureBox items.",
                    "NoS/NoD and inside/outside bars are returned as markers.",
                ],
            },
        )


def analyze_tlp_structure(
    candles: Iterable[Candle | dict[str, Any]], config: Optional[TLPConfig] = None
) -> dict[str, Any]:
    """Convenience wrapper for API endpoints."""

    return TLPSwingAnalyzer(config=config).analyze(candles).to_dict()
