from werkzeug.security import generate_password_hash, check_password_hash
from .. import db
from .base import BaseModelMixin

# 多对多关联表：用户和角色
user_role_association = db.Table(
    'user_role_association',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)


class User(BaseModelMixin, db.Model):
    """
    用户表模型
    """
    __tablename__ = 'users'

    username = db.Column(db.String(64), unique=False, nullable=False, index=True, comment='用户姓名')
    nickname = db.Column(db.String(64), comment='用户昵称')
    # 部门关联，一对多关系
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), comment='所属部门ID')
    # 联系方式
    phone_number = db.Column(db.String(32), unique=True, index=True, comment='手机号')
    email = db.Column(db.String(128), unique=True, index=True, comment='用户邮箱')
    # 认证和权限相关字段
    password = db.Column(db.String(128), nullable=False, comment='密码哈希值')
    is_admin = db.Column(db.Boolean, default=False, comment='是否为管理员')

    # 业务字段
    gender = db.Column(db.SmallInteger, comment='性别：1=男, 2=女, 0=未知')
    login_ip = db.Column(db.String(64), comment='上次登录IP')

    # 定义与 Role 模型的多对多关系，通过 user_role_association 中间表关联起来
    roles = db.relationship(
        'Role',
        secondary=user_role_association,
        backref=db.backref('users', lazy='dynamic')
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)
