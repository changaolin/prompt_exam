from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from config import Config
from flask import render_template

# 创建数据库实例
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Config.init_app(app)

    # 配置数据库
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prompt_exam.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    from .routes import main_bp, upload_bp, verify_bp, exam_bp, analysis_bp

    # 确保所有蓝图都正确注册
    app.register_blueprint(main_bp)  # 主蓝图没有 url_prefix
    app.register_blueprint(upload_bp, url_prefix='/upload')
    app.register_blueprint(verify_bp, url_prefix='/verify')
    app.register_blueprint(exam_bp, url_prefix='/exam')
    app.register_blueprint(analysis_bp, url_prefix='/analysis')

    # 确保实例文件夹存在
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # 在应用上下文中创建所有数据库表
    with app.app_context():
        db.create_all()

    # 添加错误处理
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    return app