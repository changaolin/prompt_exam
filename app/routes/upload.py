from flask import Blueprint, render_template, request, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
import os
import re
from ..models.question import Question, Option, QuestionBank
import docx
import io
import traceback
from pathlib import Path
from .. import db

upload_bp = Blueprint('upload', __name__)

def read_file_content(file):
    """读取文件内容"""
    try:
        # 获取文件扩展名
        ext = os.path.splitext(file.filename)[1].lower()

        if ext == '.docx':
            # 读取 docx 文件
            doc = docx.Document(file)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        elif ext == '.doc':
            # 如果需要处理 .doc 文件，可以添加相应的处理逻辑
            raise ValueError('暂不支持 .doc 格式，请转换为 .docx 后上传')
        else:
            raise ValueError('不支持的文件格式')

    except Exception as e:
        print(f"读取文件失败: {str(e)}")
        print(traceback.format_exc())
        raise

def parse_questions(content):
    """解析文档内容为题目列表"""
    try:
        questions = []
        current_question = None
        question_type = None

        # 分行处理内容
        lines = content.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue

            # 检查题型标记
            if "一、单选题" in line:
                question_type = "single"
                continue
            elif "二、多选题" in line:
                question_type = "multiple"
                continue
            elif "三、简答题" in line:
                question_type = "essay"
                continue

            # 处理题目
            if question_type:
                # 匹配题号和括号中的答案
                question_match = re.match(r'^(\d+)[.、]\s*(.+?)(?:\s*[（(]([A-D]+)[）)])?$', line)
                if question_match:
                    # 保存前一个题目
                    if current_question:
                        questions.append(current_question)

                    number = question_match.group(1)
                    question_text = question_match.group(2)
                    answer = question_match.group(3) or ''  # 获取括号中的答案

                    # 创建新题目
                    if question_type in ['single', 'multiple']:
                        current_question = Question(
                            number=number,
                            question=question_text,
                            type=question_type,
                            options=[],
                            answer=answer
                        )
                    else:
                        current_question = Question(
                            number=number,
                            question=question_text,
                            type=question_type,
                            options=[],
                            answer='',
                            answer_points=[]
                        )
                    continue

                # 处理选项
                if question_type in ['single', 'multiple']:
                    option_match = re.match(r'^([A-D])[.、]\s*(.+)$', line)
                    if option_match and current_question:
                        label = option_match.group(1)
                        content = option_match.group(2)
                        current_question.options.append(
                            Option(label=label, content=content)
                        )
                        continue

                    # 处理独立的答案行
                    answer_match = re.match(r'^答案[：:]\s*([A-D]+)$', line)
                    if answer_match and current_question and not current_question.answer:
                        current_question.answer = answer_match.group(1)
                        continue

                # 处理简答题答案要点
                elif question_type == 'essay' and current_question:
                    if line.startswith('答案要点'):
                        continue
                    if not hasattr(current_question, 'answer_points'):
                        current_question.answer_points = []
                    current_question.answer_points.append(line)

        # 添加最后一个题目
        if current_question:
            questions.append(current_question)

        return questions

    except Exception as e:
        print(f"解析题目失败: {str(e)}")
        print(traceback.format_exc())
        raise

@upload_bp.route('/')
def upload():
    """上传页面"""
    return render_template('upload.html')

@upload_bp.route('/process', methods=['POST'])
def process_upload():
    """处理文件上传和解析"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': '没有文件被上传'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '没有选择文件'}), 400

        if not file.filename.lower().endswith(('.doc', '.docx')):
            return jsonify({'error': '不支持的文件格式'}), 400

        # 读取文件内容
        content = read_file_content(file)

        # 解析题目
        questions = parse_questions(content)

        # 转换为字典格式
        questions_dict = []
        for q in questions:
            q_dict = {
                'number': q.number,
                'question': q.question,
                'type': q.type
            }

            if hasattr(q, 'options'):
                q_dict['options'] = [{'label': opt.label, 'content': opt.content}
                                   for opt in q.options]
            if hasattr(q, 'answer'):
                q_dict['answer'] = q.answer
            if hasattr(q, 'answer_points'):
                q_dict['answer_points'] = q.answer_points

            questions_dict.append(q_dict)

        return jsonify({
            'message': '解析成功',
            'questions': questions_dict
        })

    except Exception as e:
        print("处理上传文件时出错:")
        print(traceback.format_exc())
        return jsonify({'error': f'处理文件失败: {str(e)}'}), 500

@upload_bp.route('/example-parser')
def download_example_parser():
    """下载示例解析脚本"""
    try:
        example_parser_path = os.path.join(current_app.static_folder, 'example_parser.py')

        # 如果文件不存在，返回404
        if not os.path.exists(example_parser_path):
            return jsonify({'error': '示例解析脚本文件不存在'}), 404

        return send_file(
            example_parser_path,
            as_attachment=True,
            download_name='example_parser.py',
            mimetype='text/x-python'
        )

    except Exception as e:
        print("下载示例解析脚本时出错:", traceback.format_exc())
        return jsonify({'error': f'下载失败: {str(e)}'}), 500

@upload_bp.route('/save', methods=['POST'])
def save_questions():
    """保存题库"""
    try:
        data = request.get_json()
        if not data or 'questions' not in data:
            return jsonify({'success': False, 'error': '没有接收到题目数据'}), 400

        questions = data['questions']
        if not questions:
            return jsonify({'success': False, 'error': '题目列表为空'}), 400

        # 创建题库实例
        question_bank = QuestionBank()

        # 添加题目
        for q_data in questions:
            question = Question(
                number=q_data['number'],
                question=q_data['question'],
                type=q_data['type'],
                options=[Option(**opt) for opt in q_data.get('options', [])] if q_data.get('options') else [],
                answer=q_data.get('answer', '')
            )

            # 如果是简答题，添加答案要点
            if q_data['type'] == 'essay':
                question.answer_points = q_data.get('answer_points', [])

            question_bank.add_question(question)

        # 保存到数据库
        db.session.add(question_bank)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '题库保存成功',
            'id': question_bank.id
        })

    except Exception as e:
        print("保存题库时出错:", traceback.format_exc())
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'保存失败: {str(e)}'
        }), 500