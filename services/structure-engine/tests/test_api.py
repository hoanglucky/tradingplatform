import asyncio

from app.main import AnalyzeRequest, analyze_structure


def test_analyze_endpoint_contract_accepts_market_quality_fields() -> None:
    request = AnalyzeRequest.model_validate(
        {
            "symbol": "XAUUSD",
            "timeframe": "5m",
            "candles": [
                {
                    "timestamp": "2026-06-30T12:00:00Z",
                    "open": 3300,
                    "high": 3305,
                    "low": 3298,
                    "close": 3302,
                    "volume": 12,
                    "partial": False,
                    "complete": True,
                }
            ],
        }
    )

    result = asyncio.run(analyze_structure(request))

    assert result["metadata"]["symbol"] == "XAUUSD"
    assert result["metadata"]["timeframe"] == "5m"
    assert result["metadata"]["bars"] == 1
