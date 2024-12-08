from . import exam_bp

@exam_bp.route('/')
def index():
    return "考试页面 - 开发中" 