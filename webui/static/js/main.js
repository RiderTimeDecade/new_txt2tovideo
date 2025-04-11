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
    
    // 格式化时间
    function formatTime(timestamp) {
        if (!timestamp) return '未开始';
        return new Date(timestamp).toLocaleString('zh-CN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
    
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
                if (data.success) {
                    // 清空现有列表
                    runningTasks.innerHTML = '';
                    queuedTasks.innerHTML = '';
                    completedTasks.innerHTML = '';
                    
                    // 跟踪任务计数
                    let runningCount = 0;
                    let queuedCount = 0;
                    let completedCount = 0;
                    
                    // 处理每个任务
                    data.tasks.forEach(task => {
                        const taskElement = createTaskListItem(task);
                        if (task.status === 'processing') {
                            runningTasks.appendChild(taskElement);
                            runningCount++;
                        } else if (task.status === 'queued') {
                            queuedTasks.appendChild(taskElement);
                            queuedCount++;
                        } else if (task.status === 'completed') {
                            completedTasks.appendChild(taskElement);
                            completedCount++;
                        }
                    });
                    
                    // 显示或隐藏空状态提示
                    document.getElementById('noRunningTasks').style.display = 
                        runningCount === 0 ? 'block' : 'none';
                    document.getElementById('noQueuedTasks').style.display = 
                        queuedCount === 0 ? 'block' : 'none';
                    document.getElementById('noCompletedTasks').style.display = 
                        completedCount === 0 ? 'block' : 'none';
                }
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
        
        // 计算等待时间和处理时间
        let waitTime = '';
        let processTime = '';
        
        if (task.started_at && task.created_at) {
            const startDate = new Date(task.started_at);
            const createDate = new Date(task.created_at);
            const waitMs = startDate - createDate;
            const waitMinutes = Math.floor(waitMs / 60000);
            const waitSeconds = Math.floor((waitMs % 60000) / 1000);
            waitTime = `等待时间: ${waitMinutes}分${waitSeconds}秒`;
        }
        
        if (task.completed_at && task.started_at) {
            const completeDate = new Date(task.completed_at);
            const startDate = new Date(task.started_at);
            const processMs = completeDate - startDate;
            const processMinutes = Math.floor(processMs / 60000);
            const processSeconds = Math.floor((processMs % 60000) / 1000);
            processTime = `处理时间: ${processMinutes}分${processSeconds}秒`;
        }
        
        let html = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <h6 class="mb-1">${task.text.substring(0, 50)}${task.text.length > 50 ? '...' : ''}</h6>
                    <small class="text-muted">
                        创建时间：${formatTime(task.created_at)}<br>
                        ${task.started_at ? `开始时间：${formatTime(task.started_at)}<br>` : ''}
                        ${task.completed_at ? `完成时间：${formatTime(task.completed_at)}<br>` : ''}
                        ${waitTime ? `${waitTime}<br>` : ''}
                        ${processTime ? `${processTime}` : ''}
                    </small>
                </div>
                <span class="badge ${statusClass}">${statusText}</span>
            </div>
        `;
        
        if (task.status === 'processing') {
            html += `
                <div class="progress mt-2" style="height: 8px;">
                    <div class="progress-bar progress-bar-striped progress-bar-animated" 
                         role="progressbar" 
                         style="width: ${task.progress || 0}%">
                    </div>
                </div>
                <small class="text-muted mt-1 d-block text-end">${task.progress || 0}%</small>
            `;
        }
        
        if (task.status === 'completed' && task.file_id) {
            html += `
                <div class="mt-2 text-end">
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
                    progressBar.textContent = `${task.progress || 0}%`;
                    taskMessage.textContent = task.message || '处理中...';
                    
                    // 计算时间信息
                    let createTime = formatTime(task.created_at);
                    let startTime = task.started_at ? formatTime(task.started_at) : '等待中';
                    let completeTime = task.completed_at ? formatTime(task.completed_at) : '-';
                    
                    // 计算等待和处理时间
                    let waitTime = '';
                    let processTime = '';
                    
                    if (task.started_at && task.created_at) {
                        const startDate = new Date(task.started_at);
                        const createDate = new Date(task.created_at);
                        const waitMs = startDate - createDate;
                        const waitMinutes = Math.floor(waitMs / 60000);
                        const waitSeconds = Math.floor((waitMs % 60000) / 1000);
                        waitTime = `${waitMinutes}分${waitSeconds}秒`;
                    }
                    
                    if (task.status === 'processing' && task.started_at) {
                        const now = new Date();
                        const startDate = new Date(task.started_at);
                        const processMs = now - startDate;
                        const processMinutes = Math.floor(processMs / 60000);
                        const processSeconds = Math.floor((processMs % 60000) / 1000);
                        processTime = `${processMinutes}分${processSeconds}秒`;
                    } else if (task.completed_at && task.started_at) {
                        const completeDate = new Date(task.completed_at);
                        const startDate = new Date(task.started_at);
                        const processMs = completeDate - startDate;
                        const processMinutes = Math.floor(processMs / 60000);
                        const processSeconds = Math.floor((processMs % 60000) / 1000);
                        processTime = `${processMinutes}分${processSeconds}秒`;
                    }
                    
                    // 构建时间信息HTML
                    let timeInfoHtml = `
                        <div class="d-flex flex-wrap" style="gap: 10px;">
                            <div class="text-muted small">
                                <i class="bi bi-calendar-plus"></i> 创建时间: ${createTime}
                            </div>
                            <div class="text-muted small">
                                <i class="bi bi-play-circle"></i> 开始时间: ${startTime}
                            </div>
                    `;
                    
                    if (task.status === 'completed') {
                        timeInfoHtml += `
                            <div class="text-muted small">
                                <i class="bi bi-check-circle"></i> 完成时间: ${completeTime}
                            </div>
                        `;
                    }
                    
                    timeInfoHtml += `</div>`;
                    
                    if (waitTime || processTime) {
                        timeInfoHtml += `
                            <div class="d-flex flex-wrap mt-2" style="gap: 10px;">
                                ${waitTime ? `
                                <div class="text-muted small">
                                    <i class="bi bi-hourglass-split"></i> 等待时间: ${waitTime}
                                </div>` : ''}
                                ${processTime ? `
                                <div class="text-muted small">
                                    <i class="bi bi-lightning-charge"></i> 处理时间: ${processTime}
                                </div>` : ''}
                            </div>
                        `;
                    }
                    
                    document.getElementById('taskTimeInfo').innerHTML = timeInfoHtml;
                    
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