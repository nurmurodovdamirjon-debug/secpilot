import redis

from src.core.config import get_settings


def get_redis_client() -> redis.Redis:
    settings = get_settings()
    return redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2, socket_timeout=2)


def check_redis_ready() -> bool:
    try:
        client = get_redis_client()
        return bool(client.ping())
    except Exception:
        return False
