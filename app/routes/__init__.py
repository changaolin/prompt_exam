from flask import Blueprint, render_template

# 创建蓝图，确保 url_prefix 在这里定义
main_bp = Blueprint('main', __name__)
upload_bp = Blueprint('upload', __name__, url_prefix='/upload')
verify_bp = Blueprint('verify', __name__, url_prefix='/verify')
exam_bp = Blueprint('exam', __name__, url_prefix='/exam')
analysis_bp = Blueprint('analysis', __name__, url_prefix='/analysis')

# 导入路由处理函数
from . import upload, verify, exam, analysis

@main_bp.route('/')
def index():
    """显示主页"""
    return render_template('index.html')

# 确保其他蓝图中的路由都已注册
from .upload import *
from .verify import *
from .exam import *
from .analysis import *