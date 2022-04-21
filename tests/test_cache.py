import pytest
from web_portal.cache import CachedData


class TestCache:
    def test_empty(self):
        cache = CachedData()
        assert cache.get_cache() is None

    def test_usage(self):
        test_data = "hello world"
        cache = CachedData()
        cache.set_cache(test_data)
        assert cache.get_cache() == test_data

    def test_reset(self):
        test_data = "hello world"
        cache = CachedData()
        cache.set_cache(test_data)
        cache.reset_cache()
        assert cache.get_cache() == None
