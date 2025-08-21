from .. import db
from .base import BaseModelMixin


class Post(BaseModelMixin, db.Model):
    """
    岗位表模型
    """
    __tablename__ = 'posts'

    # 额外字段
    post_code = db.Column(db.String(64), unique=True, index=True, nullable=False, comment='岗位编码')
    name = db.Column(db.String(64), index=True, nullable=False, comment='岗位名称')

    def __repr__(self):
        return f'<Post {self.name}>'
