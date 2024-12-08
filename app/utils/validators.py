from typing import List, Dict, Any
import re

class QuestionValidator:
    """题目验证器"""

    @staticmethod
    def validate_question_format(question: Dict[str, Any]) -> List[str]:
        """验证单个题目格式"""
        errors = []

        # 基本字段验证
        required_fields = ['number', 'question', 'type']
        for field in required_fields:
            if field not in question:
                errors.append(f'缺少必要字段: {field}')

        if not errors:
            q_type = question['type']

            # 选择题验证
            if q_type in ['single', 'multiple']:
                if 'options' not in question or not isinstance(question['options'], list):
                    errors.append('选择题必须包含选项列表')
                elif len(question['options']) < 4:
                    errors.append('选择题选项数量不足')
                else:
                    # 验证选项格式
                    for i, opt in enumerate(question['options']):
                        if not isinstance(opt, dict):
                            errors.append(f'选项 {i+1} ���式错误')
                        elif 'label' not in opt or 'content' not in opt:
                            errors.append(f'选项 {i+1} 缺少标签或内容')

                # 验证答案格式
                if 'answer' not in question or not question['answer']:
                    errors.append('选择题必须包含答案')
                elif q_type == 'single' and not re.match(r'^[A-D]$', question['answer']):
                    errors.append('单选题答案必须是单个大写字母A-D')
                elif q_type == 'multiple' and not re.match(r'^[A-D]+$', question['answer']):
                    errors.append('多选题答案必须是大写字母A-D的组合')

            # 简答题验证
            elif q_type == 'essay':
                if 'answer_points' not in question or not isinstance(question['answer_points'], list):
                    errors.append('简答题必须包含答案要点列表')
                elif not question['answer_points']:
                    errors.append('简答题答案要点不能为空')

            else:
                errors.append(f'未知的题目类型: {q_type}')

        return errors

    @staticmethod
    def validate_questions_count(questions: List[Dict[str, Any]]) -> List[str]:
        """验证题目数量"""
        errors = []

        # 统计��类型题目数量
        counts = {
            'single': len([q for q in questions if q['type'] == 'single']),
            'multiple': len([q for q in questions if q['type'] == 'multiple']),
            'essay': len([q for q in questions if q['type'] == 'essay'])
        }

        # 验证数量是否符合要求
        if counts['single'] != 40:
            errors.append(f'单选题数量不正确: 期望40题，实际{counts["single"]}题')
        if counts['multiple'] != 40:
            errors.append(f'多选题数量不正确: 期望40题，实际{counts["multiple"]}题')
        if counts['essay'] != 2:
            errors.append(f'简答题数量不正确: 期望2题，实际{counts["essay"]}题')

        return errors

    @staticmethod
    def validate_all(questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """验证所有题目"""
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }

        # 验证题目数量
        count_errors = QuestionValidator.validate_questions_count(questions)
        if count_errors:
            result['warnings'].extend(count_errors)

        # 验证每个题目的格式
        for i, question in enumerate(questions):
            errors = QuestionValidator.validate_question_format(question)
            if errors:
                result['errors'].append({
                    'question_index': i,
                    'question_number': question.get('number', f'题目{i+1}'),
                    'errors': errors
                })

        if result['errors']:
            result['is_valid'] = False

        return result