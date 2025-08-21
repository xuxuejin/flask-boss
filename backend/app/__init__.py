from flask import Flask
from redis import Redis
from .config import get_config
from .utils.logger import setup_logger
from .views import register_blueprints
from .extensions import db, setup_extensions


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config())

    # print(app.config)

    # 初始化日志
    setup_logger(app)

    # 初始化数据库
    try:
        db.init_app(app)
        setup_extensions(app)
    except Exception as e:
        app.logger.error(f"Database initialization failed: {e}")
        # 如果数据库初始化失败，则抛出异常，阻止应用启动
        raise

    # 初始化 Redis 客户端，使用 from_url() 方法从配置中加载URI
    try:
        redis_client = Redis.from_url(app.config['REDIS_URI'])
        app.redis_client = redis_client
    except Exception as e:
        app.logger.error(f"Redis initialization failed: {e}")
        raise

    # 注册蓝图
    register_blueprints(app)

    # 注册 CLI 命令
    from .commands import init_db_command
    app.cli.add_command(init_db_command)

    return app
