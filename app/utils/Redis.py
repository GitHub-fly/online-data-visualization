from flask import current_app
import redis


class Redis(object):
    """
    redis数据库操作
    """

    @staticmethod
    def _get_redis_conn():
        host = current_app.config['REDIS_HOST']
        port = current_app.config['REDIS_PORT']
        db = current_app.config['REDIS_DB']
        r = redis.StrictRedis(host, port, db)
        return r

    @classmethod
    def write(cls, key, value, expire=None):
        """
        写入键值对
        """
        # 判断是否有过期时间，没有就设置默认值
        if expire:
            expire_in_seconds = expire
        else:
            expire_in_seconds = current_app.config['REDIS_EXPIRE']
        r = cls._get_redis_conn()
        r.set(key, value, ex=expire_in_seconds)

    @classmethod
    def read(cls, key):
        """
        读取键值对内容
        """
        r = cls._get_redis_conn()
        value = r.get(key)
        return value.decode('utf-8') if value else value

    @classmethod
    def hset(cls, name, key, value):
        """
        写入hash表
        """
        r = cls._get_redis_conn()
        r.hset(name, key, value)

    @classmethod
    def hmset(cls, key, *value):
        """
        读取指定hash表的所有给定字段的值
        """
        r = cls._get_redis_conn()
        value = r.hmset(key, *value)
        return value

    @classmethod
    def hget(cls, name, key):
        """
        读取指定hash表的键值
        """
        r = cls._get_redis_conn()
        value = r.hget(name, key)
        return value.decode('utf-8') if value else value

    @classmethod
    def hgetall(cls, name):
        """
        获取指定hash表所有的值
        """
        r = cls._get_redis_conn()
        return r.hgetall(name)

    @classmethod
    def delete(cls, *names):
        """
        删除一个或者多个
        """
        r = cls._get_redis_conn()
        r.delete(*names)

    @classmethod
    def hdel(cls, name, key):
        """
        删除指定hash表的键值
        :param name:
        :param key:
        :return:
        """
        r = cls._get_redis_conn()
        r.hdel(name, key)

    @classmethod
    def expire(cls, name, expire=None):
        """
        设置过期时间
        """
        if expire:
            expire_in_seconds = expire
        else:
            expire_in_seconds = current_app.config['REDIS_EXPIRE']
        r = cls._get_redis_conn()
        r.expire(name, expire_in_seconds)