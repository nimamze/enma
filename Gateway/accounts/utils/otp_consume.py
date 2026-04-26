from django.core.cache import cache


def consume_otp_authorization(user_phone, purpose):
    limit_key = f"otp_consume_limit:{purpose}:{user_phone}"
    attempts = cache.incr(limit_key)
    if attempts == 1:
        cache.expire(limit_key, 20)  # type: ignore
    if attempts > 5:
        return False
    key = f"can_{purpose}:{user_phone}"
    result = cache.get(key)
    if result:
        cache.delete(key)
        return True
    return False
