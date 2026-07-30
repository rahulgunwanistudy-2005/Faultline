from faultline_api.services.rate_limit import SlidingWindowLimiter


def test_limiter_enforces_window_limit() -> None:
    limiter = SlidingWindowLimiter(limit=2, window_seconds=60, max_keys=4)
    assert limiter.allow("client:write") is True
    assert limiter.allow("client:write") is True
    assert limiter.allow("client:write") is False


def test_limiter_key_store_is_bounded() -> None:
    limiter = SlidingWindowLimiter(limit=2, window_seconds=60, max_keys=2)
    assert limiter.allow("client-a") is True
    assert limiter.allow("client-b") is True
    assert limiter.allow("client-c") is False
    assert len(limiter._events) == 2
