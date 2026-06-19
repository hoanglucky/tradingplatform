import app.models  # noqa: F401
from app.db.base import Base


def test_core_model_tables_are_registered() -> None:
    assert {"users", "symbols", "candles", "watchlists", "watchlist_items"}.issubset(Base.metadata.tables)


def test_candle_constraints_are_registered() -> None:
    candle_table = Base.metadata.tables["candles"]

    assert "ix_candles_symbol_timeframe_timestamp" in {index.name for index in candle_table.indexes}
    assert "uq_candles_symbol_timeframe_timestamp" in {
        constraint.name for constraint in candle_table.constraints
    }
