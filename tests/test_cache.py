from app.cache import AnswerCache


def test_cache_stores_and_retrieves():
    cache = AnswerCache()

    cache.set("question", "answer")

    assert cache.get("question") == "answer"


def test_cache_lru_eviction():
    cache = AnswerCache(max_size=2)

    cache.set("q1", "a1")
    cache.set("q2", "a2")

    cache.get("q1")

    cache.set("q3", "a3")

    assert cache.get("q1") == "a1"
    assert cache.get("q2") is None
    assert cache.get("q3") == "a3"