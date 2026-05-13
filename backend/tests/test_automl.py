from core.automl_engine import _build_confidence, _trend_label


def test_trend_label_thresholds():
    assert _trend_label(2.0) == "upward"
    assert _trend_label(-2.0) == "downward"
    assert _trend_label(0.2) == "sideways"


def test_confidence_returns_structured_label():
    confidence = _build_confidence(rmse=1.5, last_close=100.0, trend="upward", sentiment_score=1.0)
    assert confidence["label"] in {"Low", "Medium", "High"}
    assert 0.0 <= confidence["score"] <= 1.0
    assert "RMSE" in confidence["rationale"]
