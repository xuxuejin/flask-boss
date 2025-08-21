import click
from flask.cli import with_appcontext
from .models.user import User
from .extensions import db


@click.command('init-db')
@with_appcontext
def init_db_command():
    """
    初始化数据库，创建所有表，并初始化一个超级管理员。
    """
    # 在应用上下文中执行数据库操作
    db.create_all()

    # 检查是否已有用户，如果没有，则创建超级管理员
    if User.query.filter_by(username='boss').first() is None:
        admin_user = User(
            username='boss',
            is_admin=True
        )
        admin_user.set_password('boss')  # 设置密码并哈希
        db.session.add(admin_user)
        db.session.commit()
        click.echo("Initial admin user created successfully.")
    else:
        click.echo("Admin user already exists.")

    click.echo("Database tables created successfully.")
