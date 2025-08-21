from .. import db
from .base import BaseModelMixin


class Department(BaseModelMixin, db.Model):
    """
    部门表模型
    """
    __tablename__ = 'departments'

    # 基本字段
    name = db.Column(db.String(64), unique=True, index=True, nullable=False, comment='部门名称')

    # 自引用字段，用于构建树状结构
    parent_id = db.Column(db.Integer, db.ForeignKey('departments.id'), comment='上级部门ID')

    # 定义与 User 模型的关系
    users = db.relationship('User', backref='department', lazy='dynamic')

    # 定义自引用关系，用于获取子部门
    children = db.relationship(
        'Department',
        backref=db.backref('parent', remote_side='Department.id'),  # 修复这里
        lazy='dynamic'
    )

    def __repr__(self):
        return f'<Department {self.name}>'
