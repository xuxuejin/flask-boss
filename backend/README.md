## 项目结构
flask-boss/
├── .gitignore               # Git 忽略文件
├── .python-version          # 指定 Python 版本
├── .venv/                   # 虚拟环境目录
├── README.md                # 项目文档
├── pyproject.toml           # 项目配置，包含依赖和元数据
├── uv.lock                  # 锁文件
├── config.toml              # 静态配置数据
├── app/                     # 主包，包含 Flask 应用核心代码
│   ├── __init__.py          # 初始化 Flask 应用、配置和蓝图
│   ├── config.py            # 配置文件
│   ├── models/              # 数据库模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── ...
│   ├── views/               # 蓝图模块
│   │   ├── __init__.py
│   │   ├── auth.py          # 认证相关蓝图
│   │   ├── api.py           # API 相关蓝图
│   │   └── ...
│   ├── static/              # 静态文件
│   ├── templates/           # 模板文件
│   └── utils/               # 工具模块
├── db/                      # 数据库
│   ├── schema/              
│   │   ├── init_db.sql      # 数据库初始化 SQL 脚本
│   │   └── ...
│   └── ...
├── scripts/                 
│   ├── deploy.sh            # 部署脚本
│   ├── backup.sh            # 数据填充 SQL 脚本
│   └── ...
├── tests/                   # 测试目录
│   ├── unit/                # 单元测试            
│   ├── integration          # 集成测试 
│   └── ...
└── app.py                   # 项目启动入口

## 超管账号
- name:boss
- pwd:boss

## 建表基础字段
- 必须字段：id（主键）、create_time（创建时间）、update_time（更新时间）、status（状态）、is_deleted（逻辑删除）
- 可选字段：create_by（创建者）、update_by（更新者）、remark（备注）

## 生成 SECRET_KEY
- import secrets
- print(secrets.token_hex(32))

## 初始化数据库和创建超级管理员指令
- flask init-db

## 单元测试
- pytest：运行所有的测试用例
- pytest tests/test_captcha.py：只运行特定的测试文件
- pytest tests/test_captcha.py::test_validate_captcha_case_insensitivity：只运行特定测试文件中的特定方法
- pytest -v tests/test_captcha.py：查看测试详情


