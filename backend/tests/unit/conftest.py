import os
import pytest
from unittest.mock import MagicMock
import time
from backend.app import create_app


@pytest.fixture(scope="module")
def app():
    """模块级应用实例"""
    os.environ['FLASK_ENV'] = 'testing'
    app = create_app()

    # 应用特定测试配置
    # app.config.update({
    #     'TESTING': True,
    #     'CAPTCHA_EXPIRY': 300,
    # })

    with app.app_context():
        # print("setup")
        yield app  # yield 前是 setup，yield 后是 teardown。
        # print("teardown")


# 不直接导入全局的 redis_client，通过 mocker 来模拟它
@pytest.fixture
def redis_mock():
    """
    模拟 Redis 客户端，支持 set、setex、get 和 delete，并模拟过期时间。
    """
    mock_client = MagicMock()
    mock_data = {}  # 存储键值对
    mock_expiry = {}  # 存储键的过期时间

    def normalize_key(key):
        """规范化键为字符串"""
        return key.decode('utf-8') if isinstance(key, bytes) else str(key)

    def normalize_value(value):
        """规范化值为字节串，模仿 Redis 行为"""
        return value.encode('utf-8') if isinstance(value, str) else value

    def set_mock(name, value, ex=None):
        """模拟 Redis 的 set 方法"""
        key = normalize_key(name)
        value = normalize_value(value)
        mock_data[key] = value
        if ex is not None:
            if not isinstance(ex, (int, float)) or ex <= 0:
                raise ValueError("expire time must be a positive number")
            mock_expiry[key] = time.time() + ex
        return True

    def setex_mock(name, expire_time, value):
        """模拟 Redis 的 setex 方法"""
        return set_mock(name, value, ex=expire_time)

    def get_mock(name):
        """模拟 Redis 的 get 方法，检查过期时间"""
        key = normalize_key(name)
        if key in mock_expiry and time.time() > mock_expiry[key]:
            mock_data.pop(key, None)
            mock_expiry.pop(key, None)
            return None
        return mock_data.get(key)

    def delete_mock(name):
        """模拟 Redis 的 delete 方法"""
        key = normalize_key(name)
        mock_expiry.pop(key, None)
        return mock_data.pop(key, None) is not None

    mock_client.set.side_effect = set_mock
    mock_client.setex.side_effect = setex_mock
    mock_client.get.side_effect = get_mock
    mock_client.delete.side_effect = delete_mock

    return mock_client


@pytest.fixture
def client(app):
    """
    创建测试客户端 - 组合其他 Fixture
    自动注入 app 和 mock_redis_client
    """
    return app.test_client()


# @pytest.fixture
# def authenticated_client(client):
#     """已认证的测试客户端"""
#     # 先创建测试用户
#     client.post('/register', json={'username': 'test', 'password': 'pass'})
#
#     # 登录获取 token
#     response = client.post('/login', json={'username': 'test', 'password': 'pass'})
#     token = response.json['access_token']
#
#     # 设置认证头
#     client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'
#     return client
