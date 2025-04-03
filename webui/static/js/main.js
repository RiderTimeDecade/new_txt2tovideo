document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const generateForm = document.getElementById('generateForm');
    const textInput = document.getElementById('textInput');
    const voiceSelect = document.getElementById('voiceSelect');
    const generateBtn = document.getElementById('generateBtn');
    const taskCard = document.getElementById('taskCard');
    const progressBar = document.getElementById('progressBar');
    const taskMessage = document.getElementById('taskMessage');
    const downloadSection = document.getElementById('downloadSection');
    const downloadBtn = document.getElementById('downloadBtn');
    
    // 当前任务ID
    let currentTaskId = null;
    let currentFileId = null;
    
    // 加载可用的语音列表
    loadVoices();
    
    // 加载语音列表
    function loadVoices() {
        fetch('/api/voices')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // 清空选项
                    voiceSelect.innerHTML = '';
                    
                    // 添加默认选项
                    const defaultOption = document.createElement('option');
                    defaultOption.value = '';
                    defaultOption.textContent = '请选择语音';
                    defaultOption.selected = true;
                    defaultOption.disabled = true;
                    voiceSelect.appendChild(defaultOption);
                    
                    // 添加语音选项
                    for (const [name, id] of Object.entries(data.voices)) {
                        const option = document.createElement('option');
                        option.value = id;
                        option.textContent = name;
                        voiceSelect.appendChild(option);
                    }
                } else {
                    showError('加载语音列表失败: ' + data.error);
                }
            })
            .catch(error => {
                showError('加载语音列表出错: ' + error.message);
            });
    }
    
    // 表单提交处理
    generateForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 获取表单数据
        const text = textInput.value.trim();
        const voice = voiceSelect.value;
        
        // 验证表单
        if (!text) {
            showError('请输入文本');
            return;
        }
        
        if (!voice) {
            showError('请选择语音');
            return;
        }
        
        // 禁用生成按钮
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<span class="loading"></span> 处理中...';
        
        // 显示任务卡片
        taskCard.classList.remove('d-none');
        taskCard.classList.add('visible');
        progressBar.style.width = '0%';
        taskMessage.textContent = '正在提交任务...';
        downloadSection.classList.add('d-none');
        
        // 发送请求
        fetch('/api/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: text,
                voice: voice
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // 保存任务ID和文件ID
                currentTaskId = data.task_id;
                
                // 开始轮询任务状态
                pollTaskStatus();
            } else {
                showError('提交任务失败: ' + data.error);
                resetForm();
            }
        })
        .catch(error => {
            showError('提交任务出错: ' + error.message);
            resetForm();
        });
    });
    
    // 轮询任务状态
    function pollTaskStatus() {
        if (!currentTaskId) return;
        
        fetch(`/api/task/${currentTaskId}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const task = data.task;
                    
                    // 更新进度条和消息
                    progressBar.style.width = `${task.progress}%`;
                    taskMessage.textContent = task.message;
                    
                    // 保存文件ID
                    currentFileId = task.file_id;
                    
                    // 根据任务状态处理
                    if (task.status === 'completed') {
                        // 任务完成
                        generateBtn.disabled = false;
                        generateBtn.innerHTML = '<i class="bi bi-play-fill"></i> 生成视频';
                        
                        // 显示下载按钮
                        downloadSection.classList.remove('d-none');
                        downloadBtn.href = `/api/download/${currentFileId}`;
                    } else if (task.status === 'failed') {
                        // 任务失败
                        showError(task.message);
                        resetForm();
                    } else {
                        // 任务仍在处理中，继续轮询
                        setTimeout(pollTaskStatus, 2000);
                    }
                } else {
                    showError('获取任务状态失败: ' + data.error);
                    resetForm();
                }
            })
            .catch(error => {
                showError('获取任务状态出错: ' + error.message);
                resetForm();
            });
    }
    
    // 重置表单
    function resetForm() {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="bi bi-play-fill"></i> 生成视频';
    }
    
    // 显示错误消息
    function showError(message) {
        // 创建错误提示元素
        const errorAlert = document.createElement('div');
        errorAlert.className = 'alert alert-danger alert-dismissible fade show mt-3';
        errorAlert.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // 添加到表单后面
        generateForm.parentNode.insertBefore(errorAlert, generateForm.nextSibling);
        
        // 5秒后自动关闭
        setTimeout(() => {
            errorAlert.classList.remove('show');
            setTimeout(() => errorAlert.remove(), 150);
        }, 5000);
    }
}); 