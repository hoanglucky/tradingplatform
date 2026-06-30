from __future__ import annotations

from collections.abc import Iterable
from datetime import UTC, datetime

from app.schemas import AggregatedCandle, Candle
from app.timeframes import parse_timeframe


class CandleAggregationError(ValueError):
    pass


class CandleAggregator:
    def aggregate(
        self,
        candles: Iterable[Candle],
        target_timeframe: str,
        *,
        as_of: datetime | None = None,
        include_partial: bool = True,
    ) -> list[AggregatedCandle]:
        ordered = sorted(candles, key=lambda candle: candle.timestamp)
        if not ordered:
            return []

        evaluation_time = as_of or datetime.now(UTC)
        if evaluation_time.tzinfo is None or evaluation_time.utcoffset() is None:
            raise CandleAggregationError("as_of must be timezone-aware.")
        evaluation_time = evaluation_time.astimezone(UTC)

        source_symbol = ordered[0].symbol
        source_timeframe = parse_timeframe(ordered[0].timeframe)
        target = parse_timeframe(target_timeframe)
        if target.duration_milliseconds < source_timeframe.duration_milliseconds:
            raise CandleAggregationError(
                "Target timeframe cannot be smaller than the source timeframe."
            )
        if target.duration_milliseconds % source_timeframe.duration_milliseconds != 0:
            raise CandleAggregationError(
                "Target timeframe must be a multiple of the source timeframe."
            )
        if any(candle.symbol != source_symbol for candle in ordered):
            raise CandleAggregationError("All candles must use the same symbol.")
        if any(
            parse_timeframe(candle.timeframe).value != source_timeframe.value
            for candle in ordered
        ):
            raise CandleAggregationError(
                "All candles must use the same source timeframe."
            )

        buckets: dict[int, list[Candle]] = {}
        for candle in ordered:
            timestamp_milliseconds = int(candle.timestamp.timestamp() * 1000)
            if target.unit == "M":
                utc_timestamp = candle.timestamp.astimezone(UTC)
                bucket_milliseconds = int(
                    datetime(utc_timestamp.year, utc_timestamp.month, 1, tzinfo=UTC).timestamp()
                    * 1000
                )
            elif target.unit == "w":
                monday_anchor_milliseconds = int(
                    datetime(1970, 1, 5, tzinfo=UTC).timestamp() * 1000
                )
                bucket_milliseconds = (
                    (timestamp_milliseconds - monday_anchor_milliseconds)
                    // target.duration_milliseconds
                ) * target.duration_milliseconds + monday_anchor_milliseconds
            else:
                bucket_milliseconds = (
                    timestamp_milliseconds // target.duration_milliseconds
                ) * target.duration_milliseconds
            buckets.setdefault(bucket_milliseconds, []).append(candle)

        aggregated: list[AggregatedCandle] = []
        for bucket_milliseconds, bucket in sorted(buckets.items()):
            bucket_start = datetime.fromtimestamp(bucket_milliseconds / 1000, tz=UTC)
            if target.unit == "M":
                bucket_end = datetime(
                    bucket_start.year + (1 if bucket_start.month == 12 else 0),
                    1 if bucket_start.month == 12 else bucket_start.month + 1,
                    1,
                    tzinfo=UTC,
                )
            else:
                bucket_end = datetime.fromtimestamp(
                    (bucket_milliseconds + target.duration_milliseconds) / 1000,
                    tz=UTC,
                )
            closed = bucket_end <= evaluation_time
            if not include_partial and not closed:
                continue
            aggregated.append(
                AggregatedCandle(
                    symbol=source_symbol,
                    timeframe=target.value,
                    timestamp=bucket_start,
                    open=bucket[0].open,
                    high=max(candle.high for candle in bucket),
                    low=min(candle.low for candle in bucket),
                    close=bucket[-1].close,
                    volume=sum((candle.volume for candle in bucket), start=0),
                    closed=closed,
                    partial=not closed,
                )
            )
        return aggregated


def aggregate_candles(
    candles: Iterable[Candle],
    target_timeframe: str,
    *,
    as_of: datetime | None = None,
    include_partial: bool = True,
) -> list[AggregatedCandle]:
    return CandleAggregator().aggregate(
        candles,
        target_timeframe,
        as_of=as_of,
        include_partial=include_partial,
    )
