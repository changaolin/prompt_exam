from . import verify_bp

@verify_bp.route('/')
def index():
    return "题库校验页面 - 开发中" 