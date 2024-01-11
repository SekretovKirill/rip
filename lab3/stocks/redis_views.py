import redis
from django.conf import settings

def get_instance_redis():
    red =  redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
    )
    return red


def set_key(key, value):
    red = get_instance_redis()
    red.set(key, value, ex=86400)


def get_value(key):
    red = get_instance_redis()
    return red.get(key)


def delete_value(key):
    red = get_instance_redis()
    red.delete(key)