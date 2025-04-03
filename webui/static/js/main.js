document.addEventListener('DOMContentLoaded', function() {
    // 获取DOM元素
    const form = document.getElementById('generateForm');
    const textInput = document.getElementById('textInput');
    const voiceSelect = document.getElementById('voiceSelect');
    const generateBtn = document.getElementById('generateBtn');
    const taskCard = document.getElementById('taskCard');
    const progressBar = document.getElementById('progressBar');
    const taskMessage = document.getElementById('taskMessage');
    const downloadSection = document.getElementById('downloadSection');
    const downloadBtn = document.getElementById('downloadBtn');
    const errorToast = document.getElementById('errorToast');
    const errorMessage = document.getElementById('errorMessage');
    
    // 任务列表元素
    const runningTasks = document.getElementById('runningTasks');
    const queuedTasks = document.getElementById('queuedTasks');
    const completedTasks = document.getElementById('completedTasks');
    
    // 初始化变量
    let currentTaskId = null;
    let currentFileId = null;
    let taskStatusInterval = null;
    
    // 加载可用的语音选项
    function loadVoices() {
        fetch('/api/voices')
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    throw new Error(data.error);
                }
                voiceSelect.innerHTML = '<option value="" selected disabled>请选择语音...</option>';
                data.voices.forEach(voice => {
                    const option = document.createElement('option');
                    option.value = voice.id;
                    option.textContent = voice.name;
                    voiceSelect.appendChild(option);
                });
            })
            .catch(error => showError('加载语音选项失败：' + error.message));
    }
    
    // 刷新任务列表
    function refreshTaskList() {
        fetch('/api/tasks')
            .then(response => response.json())
            .then(data => {
                // 清空现有列表
                runningTasks.innerHTML = '';
                queuedTasks.innerHTML = '';
                completedTasks.innerHTML = '';
                
                // 分类显示任务
                data.tasks.forEach(task => {
                    const taskElement = createTaskListItem(task);
                    switch(task.status) {
                        case 'processing':
                            runningTasks.appendChild(taskElement);
                            break;
                        case 'queued':
                            queuedTasks.appendChild(taskElement);
                            break;
                        case 'completed':
                        case 'failed':
                            completedTasks.appendChild(taskElement);
                            break;
                    }
                });
            })
            .catch(error => console.error('刷新任务列表失败：', error));
    }
    
    // 创建任务列表项
    function createTaskListItem(task) {
        const item = document.createElement('div');
        item.className = 'list-group-item';
        
        const statusClass = {
            'queued': 'text-warning',
            'processing': 'text-primary',
            'completed': 'text-success',
            'failed': 'text-danger'
        }[task.status];
        
        const statusText = {
            'queued': '等待中',
            'processing': '处理中',
            'completed': '已完成',
            'failed': '失败'
        }[task.status];
        
        let html = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1">${task.text.substring(0, 50)}${task.text.length > 50 ? '...' : ''}</h6>
                    <small class="text-muted">创建时间：${new Date(task.created_at).toLocaleString()}</small>
                </div>
                <span class="badge ${statusClass}">${statusText}</span>
            </div>
        `;
        
        if (task.status === 'processing') {
            html += `
                <div class="progress mt-2" style="height: 5px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" 
                         style="width: ${task.progress || 0}%">
                    </div>
                </div>
            `;
        }
        
        if (task.status === 'completed' && task.file_id) {
            html += `
                <div class="mt-2">
                    <a href="/api/download/${task.file_id}" class="btn btn-sm btn-success">下载视频</a>
                </div>
            `;
        }
        
        item.innerHTML = html;
        return item;
    }
    
    // 处理表单提交
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const text = textInput.value.trim();
        const voice = voiceSelect.value;
        const imageFile = document.getElementById('imageInput').files[0];
        
        if (!text) {
            showError('请输入要转换的文本');
            return;
        }
        
        if (!voice) {
            showError('请选择语音');
            return;
        }
        
        // 禁用生成按钮
        generateBtn.disabled = true;
        
        // 显示任务卡片
        taskCard.style.display = 'block';
        progressBar.style.width = '0%';
        taskMessage.textContent = '准备中...';
        downloadSection.style.display = 'none';
        
        // 创建 FormData 对象
        const formData = new FormData();
        formData.append('text', text);
        formData.append('voice', voice);
        if (imageFile) {
            formData.append('image', imageFile);
        }
        
        // 发送生成请求
        fetch('/api/generate', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            
            currentTaskId = data.task_id;
            pollTaskStatus();
            
            // 重置表单
            textInput.value = '';
            voiceSelect.value = '';
            document.getElementById('imageInput').value = '';
            generateBtn.disabled = false;
            
            // 刷新任务列表
            refreshTaskList();
        })
        .catch(error => {
            showError(error.message);
            resetForm();
        });
    });
    
    // 轮询任务状态
    function pollTaskStatus() {
        if (taskStatusInterval) {
            clearInterval(taskStatusInterval);
        }
        
        taskStatusInterval = setInterval(() => {
            fetch(`/api/task/${currentTaskId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        throw new Error(data.error);
                    }
                    
                    const task = data.task;
                    progressBar.style.width = `${task.progress || 0}%`;
                    taskMessage.textContent = task.message || '处理中...';
                    
                    if (task.status === 'completed') {
                        clearInterval(taskStatusInterval);
                        currentFileId = task.file_id;
                        downloadSection.style.display = 'block';
                        downloadBtn.href = `/api/download/${task.file_id}`;
                        refreshTaskList();
                    } else if (task.status === 'failed') {
                        clearInterval(taskStatusInterval);
                        showError(task.message || '任务处理失败');
                        resetForm();
                        refreshTaskList();
                    }
                })
                .catch(error => {
                    clearInterval(taskStatusInterval);
                    showError(error.message);
                    resetForm();
                });
        }, 1000);
    }
    
    // 重置表单状态
    function resetForm() {
        generateBtn.disabled = false;
        taskCard.style.display = 'none';
        currentTaskId = null;
        currentFileId = null;
        document.getElementById('imageInput').value = '';
    }
    
    // 显示错误信息
    function showError(message) {
        errorMessage.textContent = message;
        const toast = new bootstrap.Toast(errorToast);
        toast.show();
    }
    
    // 初始化
    loadVoices();
    refreshTaskList();
    
    // 定期刷新任务列表
    setInterval(refreshTaskList, 5000);
}); 