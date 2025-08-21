from enum import Enum, unique
from functools import wraps
from flask import jsonify, make_response


class ResponseCode(Enum):
    """
    业务响应状态码枚举，每个成员包含一个元组：(业务码, 默认消息, HTTP 状态码)
    """
    SUCCESS = (0, "操作成功", 200)
    BAD_REQUEST = (1001, "请求参数错误", 400)
    UNAUTHORIZED = (1002, "未授权访问", 401)
    NOT_FOUND = (1003, "资源不存在", 404)
    INTERNAL_ERROR = (5001, "服务器内部错误", 500)

    # 业务自定义状态码示例
    USER_NOT_FOUND = (1004, "用户不存在", 200)
    INVALID_CAPTCHA = (1005, "验证码错误", 200)


class ApiResponse:
    # 静态方法适合定义那些逻辑上属于类但不依赖类或实例状态的辅助功能
    @staticmethod
    def _create_response(code, message, http_status_code, data):  # _ 表示该方法是“内部”或“私有”
        response_data = {
            'code': code,
            'message': message,
            'data': data
        }
        return response_data, http_status_code

    @classmethod
    def success(cls, data=None, message=None):
        code, default_message, http_status_code = ResponseCode.SUCCESS.value
        msg = message if message is not None else default_message
        return cls._create_response(code, msg, http_status_code, data)

    @classmethod
    def error(cls, response_code, data=None, message=None):
        code, default_message, http_status_code = response_code.value
        msg = message if message is not None else default_message
        return cls._create_response(code, msg, http_status_code, data)


def uniform_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 调用原始视图函数
        result = func(*args, **kwargs)

        # 如果返回值已经是一个 Flask Response 对象，则直接返回
        if isinstance(result, (jsonify.__wrapped__, )) or result is None:
            return result

        # 如果返回值是一个元组 (data, http_status_code)
        if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], int):
            data, status_code = result
            # 自动封装为成功响应
            return make_response(jsonify(ApiResponse.success(data)[0]), status_code)

        # 如果返回值是 (data, message)，则封装为成功响应，默认 HTTP 状态码为 200
        if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], str):
            data, message = result
            data, status_code = ApiResponse.success(data, message)
            return make_response(jsonify(data), status_code)

        # 否则，将原始数据封装为成功的响应
        data, status_code = ApiResponse.success(data=result)
        return make_response(jsonify(data), status_code)

    return wrapper
