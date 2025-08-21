from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from sqlalchemy import SQLAlchemyError
import redis
from backend.app import Captcha
from backend.app import limiter, db
from backend.app import User


auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/captcha', methods=['POST'])
@limiter.limit("10 per minute")  # 限制为每分钟 10 次
def get_captcha():
    """
    生成并返回验证码图片
    """
    try:
        # 使用 Captcha 类生成验证码
        captcha_gen = Captcha(current_app.redis_client)
        captcha_id, base64_data = captcha_gen.generate_captcha_base64()
    except redis.exceptions.ConnectionError:
        current_app.logger.error("Failed to connect to Redis for captcha generation.")
        return jsonify({"message": "获取验证码失败，服务器内部错误。"}), 500
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred during captcha generation: {e}")
        return jsonify({"message": "获取验证码失败，请稍后重试。"}), 500

    if not captcha_id:
        return jsonify({"error": "Failed to generate captcha"}), 500

    return jsonify({'code': 0, 'data': {'img': base64_data, 'uuid': captcha_id}, 'message': 'success'})


@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per 1 minute")  # 为登录路由添加限流，防止暴力破解
def login_user():
    """
    用户登录接口
    :return: 包含访问令牌的 json 响应
    """
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    captcha_id = data.get('captcha_id')
    captcha_code = data.get('captcha_code')

    if not all([username, password, captcha_id, captcha_code]):
        return jsonify({"code": -1, "data": None, "message": "用户名、密码、验证码ID和验证码是必填项。"}), 400

    try:
        # 实例化 Captcha 类
        captcha_gen = Captcha(current_app.redis_client)

        # 1. 验证码验证
        if not captcha_gen.verify_captcha(captcha_id, captcha_code):
            return jsonify({"code": -1, "data": None, "message": "验证码不正确。"}), 400

        # 2. 数据库查询和密码验证
        user = User.query.filter_by(username=username).first()

        # 验证用户是否存在且密码正确
        if user and user.check_password(user.password_hash, password):
            # 密码验证成功，生成 JWT 令牌
            access_token = create_access_token(identity=str(user.id))

            # 构造响应
            response = jsonify({"code": 0, "data": None, "message": "login successful"})

            # 将访问令牌设置到Cookie中
            set_access_cookies(response, access_token)

            return response
        else:
            return jsonify({"code": -1, "data": None, "message": "用户名或密码不正确。"}), 401
    except (redis.exceptions.ConnectionError, SQLAlchemyError):
        current_app.logger.error("Failed to connect to Redis for captcha generation.")
        db.session.rollback()
        return jsonify({"code": -1, "data": None, "message": "系统错误，请稍后再试。"}), 500
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred during captcha generation: {e}")
        return jsonify({"code": -1, "data": None, "message": "系统错误，请稍后再试。"}), 500


@auth_bp.route("/register", methods=["post"])
def register_user():
    """
    用户注册接口
    :return: JSON响应
    """
    pass


@auth_bp.route("logout", methods=["POST"])
def logout_user():
    """
    用户注销接口
    """
    response = jsonify({"msg": "Logout successful"})
    unset_jwt_cookies(response)  # Flask-JWT-Extended 提供的工具方法
    return response
    pass


@auth_bp.route("reset-password", methods=["POST"])
def reset_password():
    """
    密码重置接口，需要用户已登录并提供旧密码
    :return: JSON响应
    """
    pass


