// 考试相关的 JavaScript 代码
let timeLeft = 120 * 60; // 120分钟，转换为秒

function startTimer() {
    const timerDisplay = document.getElementById('countdown');

    const timer = setInterval(() => {
        timeLeft--;

        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;

        timerDisplay.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;

        if (timeLeft <= 300) { // 剩余5分钟时改变颜色
            timerDisplay.style.color = '#dc3545';
            if (!document.getElementById('timeWarning')) {
                const warning = document.createElement('div');
                warning.id = 'timeWarning';
                warning.textContent = '注意：考试时间即将结束！';
                warning.style.color = '#dc3545';
                warning.style.textAlign = 'center';
                warning.style.marginTop = '10px';
                document.querySelector('.exam-header').appendChild(warning);
            }
        }

        if (timeLeft <= 0) {
            clearInterval(timer);
            alert('考试时间已到！系统将自动提交您的答案。');
            submitExam();
        }
    }, 1000);

    // 保存定时器ID，以便在需要时清除
    window.examTimer = timer;
}

document.addEventListener('DOMContentLoaded', function() {
    // 加载考试题目
    loadExamQuestions();
    // 启动计时器
    startTimer();
    // 提交考试
    document.getElementById('submitExam').addEventListener('click', submitExam);
});

async function loadExamQuestions() {
    try {
        const response = await fetch('/exam/questions');
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.success && data.questions) {
            displayQuestions(data.questions);
        } else {
            throw new Error(data.error || '加载题目失败');
        }
    } catch (error) {
        console.error('Failed to load questions:', error);
        alert('加载题目失败，请刷新页面重试');
    }
}

function displayQuestions(questions) {
    const container = document.getElementById('questionContainer');

    // 按题型对题目进行分类
    const singleQuestions = questions.filter(q => q.type === 'single');
    const multipleQuestions = questions.filter(q => q.type === 'multiple');
    const essayQuestions = questions.filter(q => q.type === 'essay');

    let html = '';

    // 显示单选题
    if (singleQuestions.length > 0) {
        html += '<div class="question-section"><h2>一、单选题</h2>';
        html += singleQuestions.map((q, index) => `
            <div class="question-item" data-id="${q.id}">
                <div class="question-header">
                    <span class="question-number">${index + 1}.</span>
                    <span class="question-text">${q.question}</span>
                </div>
                <div class="options">
                    ${q.options.map(opt => `
                        <div class="option">
                            <input type="radio"
                                   id="q${q.id}_${opt.label}"
                                   name="q${q.id}"
                                   value="${opt.label}">
                            <label for="q${q.id}_${opt.label}">
                                ${opt.label}. ${opt.content}
                            </label>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
        html += '</div>';
    }

    // 显示多选题
    if (multipleQuestions.length > 0) {
        html += '<div class="question-section"><h2>二、多选题</h2>';
        html += multipleQuestions.map((q, index) => `
            <div class="question-item" data-id="${q.id}">
                <div class="question-header">
                    <span class="question-number">${index + 1}.</span>
                    <span class="question-text">${q.question}</span>
                </div>
                <div class="options">
                    ${q.options.map(opt => `
                        <div class="option">
                            <input type="checkbox"
                                   id="q${q.id}_${opt.label}"
                                   name="q${q.id}"
                                   value="${opt.label}">
                            <label for="q${q.id}_${opt.label}">
                                ${opt.label}. ${opt.content}
                            </label>
                        </div>
                    `).join('')}
                </div>
            </div>
        `).join('');
        html += '</div>';
    }

    // 显示简答题
    if (essayQuestions.length > 0) {
        html += '<div class="question-section"><h2>三、简答题</h2>';
        html += essayQuestions.map((q, index) => `
            <div class="question-item" data-id="${q.id}">
                <div class="question-header">
                    <span class="question-number">${index + 1}.</span>
                    <span class="question-text">${q.question}</span>
                </div>
                <div class="answer-area">
                    <textarea name="q${q.id}" rows="6" placeholder="请在此输入你的答案"></textarea>
                </div>
            </div>
        `).join('');
        html += '</div>';
    }

    container.innerHTML = html;
}

async function submitExam() {
    if (window.examTimer) {
        clearInterval(window.examTimer);
    }

    if (!confirm('确定要提交考试吗？提交后将无法修改答案。')) {
        // 如果取消提交，重新启动计时器
        startTimer();
        return;
    }

    // 收集答案
    const answers = {};
    const questions = document.querySelectorAll('.question-item');

    questions.forEach(q => {
        const id = q.dataset.id;
        if (q.querySelector('textarea')) {
            // 简答题
            answers[id] = q.querySelector('textarea').value;
        } else if (q.querySelector('input[type="checkbox"]')) {
            // 多选题
            const checked = Array.from(q.querySelectorAll('input[type="checkbox"]:checked'))
                .map(input => input.value);
            answers[id] = checked.join('');
        } else {
            // 单选题
            const checked = q.querySelector('input[type="radio"]:checked');
            answers[id] = checked ? checked.value : '';
        }
    });

    try {
        const response = await fetch('/exam/submit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ answers })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        if (result.success) {
            // 直接跳转到结果页面
            window.location.href = result.redirect;
        } else {
            throw new Error(result.error || '提交失败');
        }

    } catch (error) {
        console.error('Submit error:', error);
        alert('提交失败：' + error.message);
        // 如果提交失败，重新启动计时器
        startTimer();
    }
}

function createQuestionElement(question) {
    const div = document.createElement('div');
    div.className = 'question-item';
    div.dataset.id = question.id;

    let html = `
        <div class="question-type">
            ${question.type === 'single' ? '单选题' :
              question.type === 'multiple' ? '多选题' : '简答题'}
            （第${question.number}题）
        </div>
        <div class="question-text">${question.question}</div>
    `;

    if (question.type === 'single' || question.type === 'multiple') {
        html += '<div class="options">';
        question.options.forEach(option => {
            const inputType = question.type === 'single' ? 'radio' : 'checkbox';
            html += `
                <div class="option">
                    <input type="${inputType}"
                           id="q${question.id}_${option.label}"
                           name="q${question.id}"
                           value="${option.label}">
                    <label for="q${question.id}_${option.label}">
                        ${option.label}. ${option.content}
                    </label>
                </div>
            `;
        });
        html += '</div>';
    } else {
        html += `
            <div class="essay-answer">
                <textarea placeholder="请在此输入你的答案..."></textarea>
            </div>
        `;
    }

    div.innerHTML = html;
    return div;
}