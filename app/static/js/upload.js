// 全局变量声明
window.questionsData = window.questionsData || [];

// 获取题目类型的中文名称
function getQuestionTypeName(type) {
    const types = {
        'single': '单选题',
        'multiple': '多选题',
        'essay': '简答题'
    };
    return types[type] || type;
}

// 显示选择的文件名
document.getElementById('questionFile')?.addEventListener('change', function(e) {
    const fileName = e.target.files[0] ? e.target.files[0].name : '未选择文件';
    document.getElementById('selectedFile').textContent = `已选择: ${fileName}`;
});

// 处理文件上传和解析
document.getElementById('uploadForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();

    const formData = new FormData();
    const fileInput = document.getElementById('questionFile');

    if (!fileInput.files[0]) {
        alert('请选择文件');
        return;
    }

    formData.append('file', fileInput.files[0]);

    const submitButton = this.querySelector('button[type="submit"]');
    submitButton.disabled = true;
    submitButton.textContent = '上传中...';

    try {
        const response = await fetch('/upload/process', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // 存储题目数据
        window.questionsData = data.questions;

        // 显示预览部分
        document.querySelector('.preview-section').style.display = 'block';

        // 更新预览
        updatePreview();

        // 清空文件选择
        fileInput.value = '';
        document.getElementById('selectedFile').textContent = '';

    } catch (error) {
        console.error('Upload error:', error);
        alert('上传失败：' + error.message);
    } finally {
        submitButton.disabled = false;
        submitButton.textContent = '上传并解析';
    }
});

// 更新预览的函数
function updatePreview() {
    const selectedType = document.getElementById('questionTypeFilter').value;
    const filteredQuestions = selectedType === 'all' ?
        window.questionsData :
        window.questionsData.filter(q => q.type === selectedType);

    // 更新统计信息
    document.getElementById('totalQuestions').textContent = window.questionsData.length;
    document.getElementById('singleCount').textContent =
        window.questionsData.filter(q => q.type === 'single').length;
    document.getElementById('multipleCount').textContent =
        window.questionsData.filter(q => q.type === 'multiple').length;
    document.getElementById('essayCount').textContent =
        window.questionsData.filter(q => q.type === 'essay').length;

    // 更新题目列表
    const questionsList = document.getElementById('questionsList');
    questionsList.innerHTML = filteredQuestions.map((q, i) => `
        <div class="question-item" data-type="${q.type}">
            <button class="edit-btn" onclick="openEditModal(${window.questionsData.indexOf(q)})">编辑</button>
            <div class="question-header">
                <span class="question-number">${q.number}.</span>
                <span class="question-type">[${getQuestionTypeName(q.type)}]</span>
            </div>
            <div class="question-content">
                ${q.question}
                ${q.answer ? `（${q.answer}）` : ''}
            </div>
            ${q.options ? `
                <div class="options">
                    ${q.options.map(opt => `
                        <div class="option">
                            <span class="option-label">${opt.label}.</span>
                            <span class="option-content">${opt.content}</span>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
            ${q.answer ? `
                <div class="answer">
                    <strong>答案：</strong>
                    ${q.type === 'essay' ?
                        `<ul class="answer-points">
                            ${q.answer_points.map(point => `<li>${point}</li>`).join('')}
                        </ul>` :
                        `<span class="answer-content">${q.answer}</span>`
                    }
                </div>
            ` : ''}
        </div>
    `).join('');
}

// 打开编辑模态框
function openEditModal(index) {
    if (window.questionEditor) {
        window.questionEditor.openModal(window.questionsData[index], index);
    } else {
        console.error('Question editor not initialized');
    }
}

// 题目类型筛选
document.getElementById('questionTypeFilter')?.addEventListener('change', function() {
    updatePreview();
});

// 保存题库功能
document.getElementById('saveQuestions')?.addEventListener('click', async function() {
    if (!window.questionsData || window.questionsData.length === 0) {
        alert('没有可保存的题目');
        return;
    }

    try {
        const response = await fetch('/upload/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                questions: window.questionsData
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        if (result.success) {
            alert('题库保存成功！');
        } else {
            throw new Error(result.error || '保存失败');
        }

    } catch (error) {
        console.error('Save error:', error);
        alert('保存失败：' + error.message);
    }
});