import logging
from backend.app import create_app
from backend.app import setup_logger


# pytest 的内置捕获器：capsys 和 caplog
def test_logger_config(capsys):
    """测试日志配置是否正确"""
    app = create_app()

    # 设置 FLASK_ENV 配置，以模拟开发环境
    app.config['FLASK_ENV'] = 'development'

    # 调用 setup_logger 函数，使其使用最新的配置来设置日志级别
    setup_logger(app)

    # 检查日志级别
    assert app.logger.level == logging.DEBUG, "Logger level should be DEBUG in development"

    # 记录一条测试日志
    test_message = "Test log message"
    app.logger.info(test_message)

    # 捕获控制台输出
    # capsys 用于捕获标准输出(sys.stdout)和标准错误(sys.stderr)的内容
    captured = capsys.readouterr()  # capsys.readouterr() 会返回一个对象，该对象有两个属性：out 和 err
    # assert test_message in captured.out, "Log message should appear in console output"
    # 修复：断言现在检查标准错误流 (err)，而不是标准输出流 (out)
    assert test_message in captured.err, "Log message should appear in console output"

    # 检查日志格式
    assert "INFO" in captured.err, "Log level should be INFO"
    assert "test_logger.py" in captured.err, "Filename should be in log output"


def test_logger_error(caplog):
    """测试错误日志"""
    # 创建应用实例
    app = create_app()

    test_error = "Test error message"
    app.logger.error(test_error)

    assert test_error in caplog.text, "Error message should be logged"
