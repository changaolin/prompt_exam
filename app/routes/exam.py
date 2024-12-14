from flask import Blueprint, render_template, jsonify, request, session, url_for, redirect, current_app
from ..models.question import QuestionBank, Question
from random import sample
from .. import db

# 创建蓝图
exam_bp = Blueprint('exam', __name__)

# 用于临时存储考试结果的全局变量
exam_results_store = {}

@exam_bp.route('/start')
def start():
    """显示考试配置页面"""
    # 获取题库中各类型题目的数量
    latest_bank = QuestionBank.query.order_by(QuestionBank.id.desc()).first()
    question_counts = {
        'single': 0,
        'multiple': 0,
        'essay': 0
    }

    if latest_bank:
        all_questions = latest_bank.questions
        question_counts = {
            'single': len([q for q in all_questions if q.type == 'single']),
            'multiple': len([q for q in all_questions if q.type == 'multiple']),
            'essay': len([q for q in all_questions if q.type == 'essay'])
        }

    return render_template('exam.html', question_counts=question_counts)

@exam_bp.route('/configure', methods=['POST'])
def configure():
    """处理考试配置"""
    try:
        config = request.get_json()
        latest_bank = QuestionBank.query.order_by(QuestionBank.id.desc()).first()

        if not latest_bank:
            return jsonify({
                'success': False,
                'error': '没有可用的题库'
            }), 400

        all_questions = latest_bank.questions
        available_counts = {
            'single': len([q for q in all_questions if q.type == 'single']),
            'multiple': len([q for q in all_questions if q.type == 'multiple']),
            'essay': len([q for q in all_questions if q.type == 'essay'])
        }

        # 验证配置
        single_count = min(max(0, config.get('singleCount', 10)), min(20, available_counts['single']))
        multiple_count = min(max(0, config.get('multipleCount', 5)), min(10, available_counts['multiple']))
        essay_count = min(max(0, config.get('essayCount', 1)), min(3, available_counts['essay']))
        duration = min(max(30, config.get('duration', 120)), 180)

        # 存储配置到session
        session['exam_config'] = {
            'single_count': single_count,
            'multiple_count': multiple_count,
            'essay_count': essay_count,
            'duration': duration
        }

        return jsonify({
            'success': True,
            'redirect': url_for('exam.exam_page')
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@exam_bp.route('/page')
def exam_page():
    """显示考试页面"""
    config = session.get('exam_config', {
        'single_count': 10,
        'multiple_count': 5,
        'essay_count': 1,
        'duration': 120
    })

    return render_template('exam_page.html', **config)

@exam_bp.route('/questions')
def get_questions():
    """获取考试题目"""
    try:
        # 从session获取配置
        config = session.get('exam_config', {
            'single_count': 10,
            'multiple_count': 5,
            'essay_count': 1,
            'duration': 120
        })

        # 获取最新的题库
        latest_bank = QuestionBank.query.order_by(QuestionBank.id.desc()).first()

        if not latest_bank:
            return jsonify({'error': '没有可用的题库'}), 404

        # 从题库中选择题目
        all_questions = latest_bank.questions

        # 按题型分类
        single_choice = [q for q in all_questions if q.type == 'single']
        multiple_choice = [q for q in all_questions if q.type == 'multiple']
        essay = [q for q in all_questions if q.type == 'essay']

        # 随机选择题目
        selected_questions = []
        question_numbers = {}
        current_number = 1

        # 添加单选题
        if single_choice and config['single_count'] > 0:
            single_selected = sample(single_choice, min(config['single_count'], len(single_choice)))
            for q in single_selected:
                question_dict = {
                    'id': q.id,
                    'number': current_number,
                    'type': 'single',
                    'question': q.question,
                    'options': [
                        {'label': opt.label, 'content': opt.content}
                        for opt in q.options
                    ]
                }
                question_numbers[str(q.id)] = current_number
                current_number += 1
                selected_questions.append(question_dict)

        # 添加多选题
        if multiple_choice and config['multiple_count'] > 0:
            multiple_selected = sample(multiple_choice, min(config['multiple_count'], len(multiple_choice)))
            for q in multiple_selected:
                question_dict = {
                    'id': q.id,
                    'number': current_number,
                    'type': 'multiple',
                    'question': q.question,
                    'options': [
                        {
                            'label': opt.label,
                            'content': opt.content.strip()  # 确保去除多余空白
                        }
                        for opt in q.options
                    ]
                }
                question_numbers[str(q.id)] = current_number
                current_number += 1
                selected_questions.append(question_dict)

        # 添加简答题
        if essay and config['essay_count'] > 0:
            essay_selected = sample(essay, min(config['essay_count'], len(essay)))
            for q in essay_selected:
                question_dict = {
                    'id': q.id,
                    'number': current_number,
                    'type': 'essay',
                    'question': q.question
                }
                question_numbers[str(q.id)] = current_number
                current_number += 1
                selected_questions.append(question_dict)

        # 存储题目编号映射到session
        session['question_numbers'] = question_numbers

        return jsonify({
            'success': True,
            'questions': selected_questions
        })

    except Exception as e:
        print("获取考试题目时出错:", str(e))
        return jsonify({
            'error': '获取题目失败'
        }), 500

@exam_bp.route('/submit', methods=['POST'])
def submit_exam():
    """���交考试答案"""
    try:
        data = request.get_json()
        if not data or 'answers' not in data:
            return jsonify({'success': False, 'error': '没有接收到答案数据'}), 400

        answers = data['answers']
        question_numbers = session.get('question_numbers', {})

        print("Question numbers from session:", question_numbers)  # 调试信息

        # 获取题目和正确答案
        total_score = 0
        results = []

        for question_id, user_answer in answers.items():
            question = Question.query.get(int(question_id))
            if not question:
                continue

            # 获取题目编号，使用字符串类型的ID作为键
            question_number = question_numbers.get(str(question_id))
            print(f"Question ID: {question_id}, Number: {question_number}")  # 调试信息

            result = {
                'id': question.id,
                'number': question_number,
                'type': question.type,
                'question': question.question,
                'user_answer': user_answer,
                'correct_answer': question.answer,
                'score': 0
            }

            # 添加选项信息（如果是选择题）
            if question.type in ['single', 'multiple']:
                result['options'] = [
                    {'label': opt.label, 'content': opt.content}
                    for opt in question.options
                ]

            # 评分逻辑
            if question.type == 'single':
                if user_answer == question.answer:
                    result['score'] = 2
                    total_score += 2
            elif question.type == 'multiple':
                if set(user_answer) == set(question.answer):
                    result['score'] = 4
                    total_score += 4
            elif question.type == 'essay':
                result['answer_points'] = question.answer_points
                result['score'] = 0

            results.append(result)

        # 按题号排序
        results.sort(key=lambda x: x['number'])

        # 存储结果
        import uuid
        result_id = str(uuid.uuid4())
        exam_results_store[result_id] = {
            'results': results,
            'total_score': total_score
        }

        return jsonify({
            'success': True,
            'message': '考试提交成功',
            'redirect': url_for('exam.show_result', result_id=result_id)
        })

    except Exception as e:
        print("提交考试答案时出错:", str(e))
        return jsonify({
            'success': False,
            'error': f'提��失败: {str(e)}'
        }), 500

@exam_bp.route('/result/<result_id>')
def show_result(result_id):
    """显示考试结果"""
    try:
        # 从全局变量获取结果
        exam_data = exam_results_store.get(result_id)

        if not exam_data:
            print("No results found for ID:", result_id)
            return redirect(url_for('main.index'))

        # 渲染结果页面
        return render_template('exam_result.html',
                             results=exam_data['results'],
                             total_score=exam_data['total_score'])

    except Exception as e:
        print("显示考试结果时出错:", str(e))
        return redirect(url_for('main.index'))