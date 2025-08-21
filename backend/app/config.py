import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    # 从环境变量中获取 Redis URI，如果不存在则使用本地默认值
    REDIS_URI = os.getenv("REDIS_URI", 'redis://10.1.8.13:6379/0')

    SECRET_KEY = os.getenv("SECRET_KEY")

    # JWT 配置信息
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = os.getenv("JWT_ACCESS_TOKEN_EXPIRES", '15m')

    # --- MySQL 连接池配置 ---
    # 连接池大小，默认为 10
    SQLALCHEMY_POOL_SIZE = int(os.getenv('SQLALCHEMY_POOL_SIZE', 10))
    # 连接池溢出数量，默认为 5
    SQLALCHEMY_MAX_OVERFLOW = int(os.getenv('SQLALCHEMY_MAX_OVERFLOW', 5))


def get_config():
    config_obj = Config()

    db_type = os.getenv('DB_TYPE', 'sqlite')

    if db_type == 'sqlite':
        # SQLite 配置，从环境变量获取或使用默认值。
        sqlite_uri = os.getenv(
            'SQLALCHEMY_DATABASE_URI',
            f'sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "db/boss.db"))}'
        )
        config_obj.SQLALCHEMY_DATABASE_URI = sqlite_uri
    elif db_type == 'mysql':
        # MySQL 配置，需要从多个环境变量构建URI。
        mysql_user = os.getenv('MYSQL_USER')
        mysql_password = os.getenv('MYSQL_PASSWORD')
        mysql_host = os.getenv('MYSQL_HOST')
        mysql_port = os.getenv('MYSQL_PORT', '3306')
        mysql_db = os.getenv('MYSQL_DB')

        # 确保MySQL所需的环境变量已设置
        if not all([mysql_user, mysql_password, mysql_host, mysql_db]):
            raise ValueError("Missing one or more required MySQL environment variables (MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DB)")

        config_obj.SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"
        )
    else:
        raise ValueError(f"Invalid DB_TYPE: {db_type}. Must be 'sqlite' or 'mysql'.")

    return config_obj
