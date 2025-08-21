from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager, exceptions
from werkzeug.exceptions import TooManyRequests
from flask import jsonify
from .utils.parse_time import parse_expire_time

# 在这里实例化所有扩展对象
db = SQLAlchemy()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"]  # 设置默认的全局限速，例如每分钟100次
)

jwt = JWTManager()


def setup_extensions(app):
    """
    负责初始化所有扩展，并为应用注册错误处理函数。
    """
    # 初始化令牌
    app.config["JWT_SECRET_KEY"] = app.config['JWT_SECRET_KEY']
    # app.config["JWT_TOKEN_LOCATION"] = ["cookies"]
    # app.config["JWT_COOKIE_SECURE"] = True

    expire_str = app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = parse_expire_time(expire_str)  # 设置 token 过期时间
    jwt.init_app(app)
    # 初始化限流器
    # 将 Redis URI 添加到应用配置中，供 Limiter 使用
    app.config['RATELIMIT_STORAGE_URI'] = app.config['REDIS_URI']
    limiter.init_app(app)

    # JWT 错误处理，捕获无效令牌错误，返回 JSON 响应
    @app.errorhandler(exceptions.JWTExtendedException)
    def handle_invalid_jwt_error(error):
        app.logger.error(f"Rate limit exceeded: {error.description}")
        return jsonify({"message": "无效令牌"}), 401

    # 为 TooManyRequests 异常注册自定义错误处理函数
    @app.errorhandler(TooManyRequests)
    def handle_rate_limit_exceeded(error):
        app.logger.error(f"Rate limit exceeded: {error.description}")
        return jsonify({
            "error": "Too Many Requests",
            "message": error.description
        }), 429
