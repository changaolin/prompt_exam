def parse_questions(content: str) -> list:
    """
    解析文档内容，返回题目列表
    参数:
        content: str - 文档内容字符串
    返回:
        list - 题目对象列表
    """
    questions = []
    current_question = None
    question_type = None

    # 分行处理文件内容
    lines = content.split('\n')
    for line in lines:
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

        # 处理选择题
        if question_type in ["single", "multiple"]:
            # 匹配题目
            question_match = re.match(r'^(\d+)[.、]\s*(.+?)(?=（[A-D]+）|$)', line)
            if question_match:
                # 保存前一个题目
                if current_question and len(current_question.get('options', [])) >= 4:
                    questions.append(current_question)

                # 提取答案（如果有）
                answer = ""
                answer_match = re.search(r'（([A-D]+)）', line)
                if answer_match:
                    answer = answer_match.group(1)
                    question_text = line[:answer_match.start()].strip()
                else:
                    question_text = question_match.group(2).strip()

                # 创建新题目
                current_question = {
                    'number': question_match.group(1),
                    'question': question_text,
                    'type': question_type,
                    'options': [],
                    'answer': answer
                }
                continue

            # 匹配选项
            option_match = re.match(r'^([A-D])[.、]\s*(.+)$', line)
            if option_match and current_question:
                current_question['options'].append({
                    'label': option_match.group(1),
                    'content': option_match.group(2).strip()
                })
                continue

        # 处理简答题
        elif question_type == "essay":
            if line.startswith("答案要点"):
                if current_question:
                    current_question['answer_points'] = []
                continue

            essay_match = re.match(r'^(\d+)[.、]\s*(.+)$', line)
            if essay_match:
                if current_question and current_question.get('answer_points'):
                    questions.append(current_question)

                current_question = {
                    'number': essay_match.group(1),
                    'question': essay_match.group(2).strip(),
                    'type': 'essay',
                    'answer_points': []
                }
            elif current_question and not line.startswith(('1.', '2.')):
                if line and not line.startswith('答案要点'):
                    current_question.setdefault('answer_points', []).append(line)

    # 保存最后一个题目
    if current_question:
        if question_type in ["single", "multiple"] and len(current_question.get('options', [])) >= 4:
            questions.append(current_question)
        elif question_type == "essay" and current_question.get('answer_points'):
            questions.append(current_question)

    return questions