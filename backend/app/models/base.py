from datetime import datetime, timezone
from .. import db


class BaseModelMixin(object):
    """
    所有数据库模型的基础类，提供了通用的基础字段。
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment="主键ID")

    # 必须字段
    # 如果直接写 default=datetime.now(timezone.utc)，这个时间会在模型类定义时就被执行，而不是在插入数据时执行
    # 所以要用 lambda 或函数名（不加括号）来延迟执行
    create_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, comment='创建时间')
    update_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False, comment='更新时间')
    status = db.Column(db.SmallInteger, default=1, nullable=False, comment='状态：1=启用, 0=禁用')
    is_delete = db.Column(db.Boolean, default=False, nullable=False, comment='逻辑删除：True=已删除, False=未删除')

    # 可选字段
    create_by = db.Column(db.String(46), comment='创建者')
    update_by = db.Column(db.String(46), comment='更新者')
    remark = db.Column(db.String(256), comment='备注')

