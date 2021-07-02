"""
    整个项目所需要的配置
"""
import redis

redis_store = redis.Redis(host='47.106.128.152', port=6379, db=1)  # 操作的redis配置
host = 'rm-bp1itj68te5655569ro.mysql.rds.aliyuncs.com'
# host = '127.0.0.1'


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "onlinedatevisualization"
    # flask-session配置
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True  # 对cookie中session_id进行隐藏处理 加密混淆
    PERMANENT_SESSION_LIFETIME = 60 * 5  # session数据的有效期，单位秒


# 开发环境
class DevelopmentConfig(Config):
    """开发模式的配置信息"""
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://xiaowo_root:Xiaowo_mysql@{host}:3306/db_online_data_visualization?charset=utf8'
    # SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://root:root@{host}:3306/db_online_data_visualization?charset=utf8'
    SESSION_REDIS = redis.Redis(host='127.0.0.1', port=6379, password="root", db=2)  # 操作的redis配置
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True    # 自动提交 commit记录
    # SQLALCHEMY_ECHO = True  # 显示数据库语句
    DEBUG = True


# 线上环境
class ProductionConfig(Config):
    """生产环境配置信息"""
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123321@localhost:5433/postgres'
    # SESSION_REDIS = redis.Redis(host='xxx.com', port=6379, password="root", db=3)  # 操作的redis配置


config_map = {
    "develop": DevelopmentConfig,
    "product": ProductionConfig
}
