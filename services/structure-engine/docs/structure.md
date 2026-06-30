# TLP Swing Chart — PineScript to Python Conversion

## Source

Converted from `TLP_SWING_INDICATORS_TRADINGVIEW.txt`.

The original PineScript contains:

- TLP swing line logic
- Inside bar / outside bar marking
- Inside-bar consolidation boxes
- NoS / NoD markers

## Target architecture

The converted code is designed for:

```txt
services/structure-engine/app/structure_engine.py
```

The chart should not execute PineScript. The backend runs Python and returns overlay data:

```txt
candles
  ↓
TLPSwingAnalyzer
  ↓
swings / segments / boxes / markers
  ↓
POST /structure/analyze
  ↓
frontend chart overlay
```

## Returned overlay types

### swings

Swing highs and swing lows detected by the TLP state machine.

### segments

Line segments connecting swing points. The frontend can draw these as TLP swing lines.

### boxes

Inside-bar consolidation zones. The frontend can render these as translucent rectangles.

### markers

Markers for:

- INSIDE_BAR
- OUTSIDE_BAR
- NO_S
- NO_D
- SWING_HIGH
- SWING_LOW

## Important differences from PineScript

PineScript draws directly using `line.new`, `box.new`, `plotshape`, and `barcolor`.

Python does not draw. It returns structured data that the frontend can render.

The PineScript logic uses persistent arrays. The Python version mirrors the state machine but exposes final analysis output rather than TradingView drawing objects.

## Suggested API integration

```txt
POST /structure/analyze
```

Request:

```json
{
  "symbol": "XAUUSD",
  "timeframe": "15m",
  "model": "tlp_pine_converted",
  "start": "2026-06-01T00:00:00Z",
  "end": "2026-06-30T00:00:00Z"
}
```

Response:

```json
{
  "swings": [],
  "segments": [],
  "boxes": [],
  "markers": [],
  "metadata": {
    "source": "tlp_pine_converted"
  }
}
```

## Frontend rendering guide

- `segments` -> draw line series / custom overlay line
- `boxes` -> draw support/resistance style rectangle overlays
- `SWING_HIGH` -> marker above candle
- `SWING_LOW` -> marker below candle
- `NO_S` -> green marker below candle
- `NO_D` -> red marker above candle
- `OUTSIDE_BAR` -> blue candle state / marker
- `INSIDE_BAR` -> yellow candle state / marker

## Verification

Run tests:

```bash
docker compose --profile services run --rm structure-engine pytest
```

Minimal usage:

```python
from app.structure_engine import analyze_tlp_structure

result = analyze_tlp_structure(candles)
print(result["segments"])
```

## Frontend test

1. Start the service profile and web app.
2. Open `http://localhost:2000/dashboard/chart`.
3. Click the **Structure** button in a chart-window header.
4. Confirm that the thin blue swing line appears without point labels.

The overlay is disabled by default and analyzed independently per chart window.
