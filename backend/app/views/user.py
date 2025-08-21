from flask import Blueprint, jsonify

user_bp = Blueprint('user', __name__)


@user_bp.route('/users/me', methods=['GET'])
def get_current_user():
    """
    获取当前登录用户信息
    :return:
    """
    return jsonify({'code': 0, 'data': 'asdf', 'message': 'success'})


@user_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    获取指定用户信息
    :param user_id:
    :return:
    """


@user_bp.route('/users', methods=['GET'])
def list_users():
    """
    获取用户列表
    :return:
    """
    pass
