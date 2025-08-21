import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask


def setup_logger(app: Flask):
    log_level = logging.DEBUG if app.config.get('FLASK_ENV') == 'development' else logging.INFO

    # 创建日志文件
    log_dir = os.path.join(os.path.dirname(__file__), '../../logs')
    os.makedirs(log_dir, exist_ok=True)

    # 配置文件格式
    formatter = logging.Formatter(
        '{asctime} {filename} {levelname}: {message} [in {pathname}:{lineno}]',
        style='{'
    )
    # 修改 Flask 在 DEBUG 模式默认日志输出格式
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)

    app.logger.handlers.clear()
    app.logger.addHandler(console_handler)

    # 服务器环境记录日志文件
    if app.config.get('FLASK_ENV') != 'development':
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.log'),
            maxBytes=10_000_000,
            backupCount=5
        )
        # backupCount 指定日志文件轮转时保留的备份文件数量，app.log.1 到 app.log.5
        # 如果超过 backupCount，最早的备份文件（app.log.5）会被删除
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)

        error_handler = RotatingFileHandler(
            os.path.join(log_dir, 'error.log'),
            maxBytes=10_000_000,
            backupCount=5
        )
        error_handler.setFormatter(formatter)
        error_handler.setLevel(log_level)
        app.logger.addHandler(error_handler)

    app.logger.setLevel(log_level)
    # 获取 SQLAlchemy 引擎的日志器（sqlalchemy.engine），并将其日志级别设置为 WARNING，默认是 DEBUG 级别
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

    return app.logger
