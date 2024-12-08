class QuestionEditor {
    constructor() {
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.modal = document.getElementById('editModal');
        this.form = document.getElementById('editForm');

        if (!this.modal || !this.form) {
            console.error('Required elements not found for QuestionEditor');
            return;
        }
    }

    bindEvents() {
        if (!this.modal || !this.form) return;

        // 关闭模态框
        const closeBtn = this.modal.querySelector('.close');
        const cancelBtn = this.modal.querySelector('.cancel');

        if (closeBtn) {
            closeBtn.addEventListener('click', () => this.closeModal());
        }

        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => this.closeModal());
        }

        // 添加答案要点
        const addPointBtn = document.getElementById('addAnswerPoint');
        if (addPointBtn) {
            addPointBtn.addEventListener('click', () => this.addAnswerPoint());
        }

        // 删除答案要点的事件委托
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-point')) {
                e.target.parentElement.remove();
            }
        });

        // 表单提交
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    }

    openModal(question, index) {
        this.currentIndex = index;
        this.currentQuestion = question;

        // 设置表单值
        document.getElementById('editQuestionIndex').value = index;
        document.getElementById('editQuestionText').value = question.question;
        document.getElementById('editAnswer').value = question.answer || '';

        // 处理选项
        const optionsContainer = document.getElementById('editOptions');
        const editOptionsContainer = document.getElementById('editOptionsContainer');
        const editAnswerPoints = document.getElementById('editAnswerPoints');

        if (question.type !== 'essay') {
            optionsContainer.innerHTML = question.options.map((opt, i) => `
                <div class="form-group">
                    <label>选项 ${opt.label}:</label>
                    <div class="option-row">
                        <input type="text" class="option-input" data-label="${opt.label}"
                               value="${opt.content}" required>
                        <span class="option-label">${opt.label}</span>
                    </div>
                </div>
            `).join('');
            editOptionsContainer.style.display = 'block';
            editAnswerPoints.style.display = 'none';
        } else {
            editOptionsContainer.style.display = 'none';
            editAnswerPoints.style.display = 'block';

            const answerPointsList = document.getElementById('answerPointsList');
            answerPointsList.innerHTML = question.answer_points.map((point, i) => `
                <div class="answer-point">
                    <input type="text" value="${point}" required>
                    <button type="button" class="remove-point">删除</button>
                </div>
            `).join('');
        }

        this.modal.style.display = 'block';
    }

    closeModal() {
        this.modal.style.display = 'none';
    }

    addAnswerPoint() {
        const answerPointsList = document.getElementById('answerPointsList');
        const newPoint = document.createElement('div');
        newPoint.className = 'answer-point';
        newPoint.innerHTML = `
            <input type="text" required>
            <button type="button" class="remove-point">删除</button>
        `;
        answerPointsList.appendChild(newPoint);
    }

    handleSubmit(e) {
        e.preventDefault();

        // 更新题目内容
        this.currentQuestion.question = document.getElementById('editQuestionText').value;

        if (this.currentQuestion.type !== 'essay') {
            // 更新选项
            this.currentQuestion.options = Array.from(document.querySelectorAll('.option-input'))
                .map(input => ({
                    label: input.dataset.label,
                    content: input.value
                }));
            this.currentQuestion.answer = document.getElementById('editAnswer').value;
        } else {
            // 更新答案要点
            this.currentQuestion.answer_points = Array.from(document.querySelectorAll('#answerPointsList input'))
                .map(input => input.value)
                .filter(value => value.trim() !== '');
        }

        // 触发更新事件
        const event = new CustomEvent('questionUpdated', {
            detail: {
                index: this.currentIndex,
                question: this.currentQuestion
            }
        });
        document.dispatchEvent(event);

        this.closeModal();
    }
}

// 等待DOM加载完成后初始化编辑器
document.addEventListener('DOMContentLoaded', function() {
    // 初始化编辑器并存储到全局变量
    window.questionEditor = new QuestionEditor();

    // 输出调试信息
    console.log('QuestionEditor initialized:', window.questionEditor);
});