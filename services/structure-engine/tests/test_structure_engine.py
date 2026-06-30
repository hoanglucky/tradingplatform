from app.structure_engine import TLPConfig, analyze_tlp_structure


def c(ts, o, h, l, cl):
    return {"timestamp": ts, "open": o, "high": h, "low": l, "close": cl}


def test_empty_input_returns_empty_result():
    result = analyze_tlp_structure([])
    assert result["swings"] == []
    assert result["segments"] == []
    assert result["boxes"] == []
    assert result["markers"] == []
    assert result["metadata"]["bars"] == 0


def test_no_s_and_no_d_markers():
    candles = [
        c("t0", 10, 11, 9, 9.5),    # bearish
        c("t1", 9.4, 10.8, 8.8, 10.6),  # bullish and lower low => NO_S
        c("t2", 10.8, 11.5, 10.1, 10.2), # bearish and higher high => NO_D
    ]
    result = analyze_tlp_structure(candles)
    marker_types = {m["type"] for m in result["markers"]}
    assert "NO_S" in marker_types
    assert "NO_D" in marker_types


def test_inside_bar_zone_box_is_created_when_range_breaks():
    candles = [
        c("t0", 10, 12, 8, 11),
        c("t1", 11, 11.5, 8.5, 10),  # inside previous
        c("t2", 10, 11.2, 8.8, 10.5), # inside mother zone
        c("t3", 10.5, 12.5, 9.5, 12.2), # breaks outside
    ]
    result = analyze_tlp_structure(candles)
    assert len(result["boxes"]) == 1
    assert result["boxes"][0]["type"] == "INSIDE_BAR_ZONE"
    assert result["boxes"][0]["price_high"] == 12
    assert result["boxes"][0]["price_low"] == 8


def test_swing_segments_are_generated_for_direction_changes():
    candles = [
        c("t0", 10, 11, 9, 10),
        c("t1", 10, 12, 10, 11),
        c("t2", 11, 13, 11, 12),
        c("t3", 12, 12.5, 9.5, 10),
        c("t4", 10, 11, 8, 9),
        c("t5", 9, 12, 9.2, 11.5),
    ]
    result = analyze_tlp_structure(candles, TLPConfig(show_inside_bars=True))
    assert len(result["swings"]) >= 2
    assert len(result["segments"]) >= 1
