from . import analysis_bp

@analysis_bp.route('/')
def index():
    return "考题分析页面 - 开发中"