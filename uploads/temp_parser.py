import json
from collections import Counter

def load_questions(jsonl_path):
    """加载JSONL文件中的题目"""
    questions = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            questions.append(json.loads(line))
    return questions

def analyze_answers():
    """分析答案分布"""
    # 加载所有题目
    single_questions = load_questions('output/single_choice.jsonl')
    multiple_questions = load_questions('output/multiple_choice.jsonl')

    # 分析单选题答案分布
    single_answers = Counter(q['answer'] for q in single_questions)
    print("\n单选题答案分布:")
    for option, count in sorted(single_answers.items()):
        print(f"选项 {option}: {count}题 ({count/len(single_questions)*100:.1f}%)")

    # 分析多选题答案分布
    multiple_answer_lengths = Counter(len(q['answer']) for q in multiple_questions)
    print("\n多选题答案数量分布:")
    for length, count in sorted(multiple_answer_lengths.items()):
        print(f"{length}个选项: {count}题 ({count/len(multiple_questions)*100:.1f}%)")

    # 分析多选题中各选项出现频率
    multiple_options = []
    for q in multiple_questions:
        multiple_options.extend(list(q['answer']))
    multiple_option_freq = Counter(multiple_options)
    print("\n多选题各选项出现频率:")
    for option, count in sorted(multiple_option_freq.items()):
        print(f"选项 {option}: {count}次")

def random_paper(num_single=20, num_multiple=10, num_essay=1):
    """随机抽题组卷"""
    import random

    # 加载所有题目
    single_questions = load_questions('output/single_choice.jsonl')
    multiple_questions = load_questions('output/multiple_choice.jsonl')
    essay_questions = load_questions('output/essay.jsonl')

    # 随机抽取题目
    selected_single = random.sample(single_questions, num_single)
    selected_multiple = random.sample(multiple_questions, num_multiple)
    selected_essay = random.sample(essay_questions, num_essay)

    # 生成试卷
    print("\n=== 随机生成试卷 ===")
    print(f"\n一、单选题（每题2分，共{num_single*2}分）")
    for i, q in enumerate(selected_single, 1):
        print(f"\n{i}. {q['question']}")
        for opt in q['options']:
            print(f"{opt['label']}. {opt['content']}")

    print(f"\n二、多选题（每��3分，共{num_multiple*3}分）")
    for i, q in enumerate(selected_multiple, 1):
        print(f"\n{i}. {q['question']}")
        for opt in q['options']:
            print(f"{opt['label']}. {opt['content']}")

    print(f"\n三、简答题（每题10分，共{num_essay*10}分）")
    for i, q in enumerate(selected_essay, 1):
        print(f"\n{i}. {q['question']}")

    # 生成答案
    print("\n=== 答案 ===")
    print("\n单选题答案:")
    for i, q in enumerate(selected_single, 1):
        print(f"{i}. {q['answer']}")

    print("\n多选题答案:")
    for i, q in enumerate(selected_multiple, 1):
        print(f"{i}. {q['answer']}")

    print("\n简答题答案要点:")
    for i, q in enumerate(selected_essay, 1):
        print(f"\n{i}. {q['question']}")
        for j, point in enumerate(q['answer_points'], 1):
            print(f"   {j}) {point}")

if __name__ == "__main__":
    # 运行答案分析
    print("=== 答案分析 ===")
    analyze_answers()

    # 生成随机试卷（可以自定义题目数量）
    random_paper(num_single=20, num_multiple=10, num_essay=1) 