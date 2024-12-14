from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# 创建数据库实例
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # 设置 secret key
    app.secret_key = 'your-secret-key-here'  # 在生产环境中应使用复杂的随机字符串

    # 配置数据库
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prompt_exam.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    from .routes import main_bp, upload_bp, exam_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(exam_bp, url_prefix='/exam')

    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 在应用上下文中创建所有数据库表
    with app.app_context():
        db.create_all()

    return app