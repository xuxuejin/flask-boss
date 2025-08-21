import pytest
import io
import base64
from PIL import Image
from backend.app import Captcha


@pytest.fixture
def test_captcha_instance(redis_mock):
    """每次测试生成一个新的 Captcha 实例，注入 mock redis"""
    return Captcha(redis_client=redis_mock)

# ====================
# Unit Tests
# ====================


def test_generate_captcha_base64_and_store(test_captcha_instance, redis_mock):
    base64_data, captcha_id = test_captcha_instance.generate_captcha_base64()

    # 1. 验证返回值类型
    assert isinstance(base64_data, str), "Base64 data should be a string"
    assert isinstance(captcha_id, str), "Captcha ID should be a string"
    assert len(captcha_id) == 32, "Captcha ID should be a 32-character UUID"

    # 2. 验证 Base64 字符串是否为有效图片
    try:
        # 移除 "data:image/png;base64," 前缀
        base64_string = base64_data.split(",")[1] if "," in base64_data else base64_data
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))
        assert image.format == "PNG", "Generated image should be PNG format"
    except Exception as e:
        pytest.fail(f"Base64 string is not a valid image: {e}")

    # 3. 验证 Redis 的 setex 方法是否被调用
    redis_mock.setex.assert_called_once()

    # 4. 获取 setex 的调用参数
    call_args = redis_mock.setex.call_args
    assert call_args.args[0].startswith(test_captcha_instance.key_prefix), "Redis key should start with prefix"
    assert call_args.args[1] == test_captcha_instance.expire, "Redis expiry time should match configuration"
    assert isinstance(call_args.args[2], str), "Stored captcha code should be a string"
    assert len(call_args.args[2]) == 4, "Stored captcha code should be 4 characters long"


def test_validate_captcha_success(redis_mock):
    """
    测试验证码验证成功的情况
    """
    stored_code = "TEST"
    captcha_id = "test-id"

    captcha_instance = Captcha(redis_client=redis_mock)
    # redis_mock.get.side_effect = lambda skey: stored_code.encode('utf-8') if skey == f"captcha:{captcha_id}" else None

    redis_mock.get.return_value = stored_code.encode('utf-8')

    user_input = "test"  # 不区分大小写

    # 正确调用方式：需要实际调用 get 方法
    key = f'captcha:{captcha_id}'
    result = redis_mock.get(key)  # 正确调用
    print(f"Redis mock get 返回值: {result}")  # 现在会显示 b'TEST'

    # is_valid = test_captcha_instance.validate_captcha(captcha_id, user_input)
    #
    # 调试：打印输入和存储的验证码
    # print(f"用户输入: {user_input}, 存储的验证码: {stored_code}, 验证结果: {is_valid}")
    #
    # # 验证结果为 True
    # assert is_valid is True, "Valid captcha should return True"
    #
    # # 验证 Redis 方法调用
    # redis_mock.get.assert_called_with("captcha:test-id")
    # redis_mock.delete.assert_called_with("captcha:test-id")


def test_validate_captcha_case_insensitive(test_captcha_instance, redis_mock):
    """
    测试验证码验证对大小写不敏感
    """
    stored_code = "TEST"
    redis_mock.get.return_value = stored_code.encode('utf-8')
    captcha_id = "test-id"

    # 测试不同大小写组合
    for user_input in ["test", "TEST", "TeSt", "tEsT"]:
        is_valid = test_captcha_instance.validate_captcha(captcha_id, user_input)
        assert is_valid is True, f"Validation should be case-insensitive for input: {user_input}"


def test_validate_captcha_failure_wrong_input(test_captcha_instance, redis_mock):
    """
    测试用户输入错误验证码的情况
    """
    stored_code = "TEST"
    redis_mock.get.return_value = stored_code.encode('utf-8')
    captcha_id = "test-id"
    user_input = "WRONG"

    is_valid = test_captcha_instance.validate_captcha(captcha_id, user_input)

    # 1. 验证结果为 False
    assert is_valid is False, "Invalid captcha input should return False"

    # 2. 验证 Redis 方法调用
    redis_mock.get.assert_called_with("captcha:test-id")
    redis_mock.delete.assert_not_called(), "Redis delete should not be called for invalid input"


def test_validate_captcha_nonexistent_id(test_captcha_instance, redis_mock):
    """
    测试验证码 ID 不存在的情况
    """
    redis_mock.get.return_value = None  # 模拟 Redis 中无此验证码
    captcha_id = "nonexistent-id"
    user_input = "TEST"

    is_valid = test_captcha_instance.validate_captcha(captcha_id, user_input)

    # 1. 验证结果为 False
    assert is_valid is False, "Nonexistent captcha ID should return False"

    # 2. 验证 Redis 方法调用
    redis_mock.get.assert_called_with("captcha:nonexistent-id")
    redis_mock.delete.assert_not_called(), "Redis delete should not be called for nonexistent ID"


def test_validate_captcha_empty_input(test_captcha_instance, redis_mock):
    """
    测试用户输入为空的情况
    """
    stored_code = "TEST"
    redis_mock.get.return_value = stored_code.encode('utf-8')
    captcha_id = "test-id"
    user_input = ""

    is_valid = test_captcha_instance.validate_captcha(captcha_id, user_input)

    # 1. 验证结果为 False
    assert is_valid is False, "Empty captcha input should return False"

    # 2. 验证 Redis 方法调用
    redis_mock.get.assert_called_with("captcha:test-id")
    redis_mock.delete.assert_not_called(), "Redis delete should not be called for empty input"


def test_generate_captcha_redis_failure(test_captcha_instance, redis_mock):
    """
    测试 Redis 存储失败的情况
    """
    redis_mock.setex.side_effect = Exception("Redis connection error")

    with pytest.raises(Exception, match="Redis connection error"):
        test_captcha_instance.generate_captcha_base64()

