from django.core.cache import cache
from rest_framework import serializers


def atomic_rate_limit(key: str, ttl: int, max_attempts: int):
    attempts = cache.incr(key)
    if attempts == 1:
        cache.expire(key, ttl)  # type: ignore
    if attempts > max_attempts:
        raise serializers.ValidationError("rate limit exceeded")
