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
    const toggleBatchMode = document.getElementById('toggleBatchMode');
    const batchOptionsSection = document.getElementById('batchOptionsSection');
    const folderInput = document.getElementById('folderInput');
    const fileList = document.getElementById('fileList');
    const singleModeOptions = document.getElementById('singleModeOptions');
    const singleModeImageUpload = document.getElementById('singleModeImageUpload');
    
    // 批量模式相关元素
    const splitByParagraph = document.getElementById('splitByParagraph');
    const splitBySentence = document.getElementById('splitBySentence');
    const maxTextLength = document.getElementById('maxTextLength');
    
    // 任务列表元素
    const runningTasks = document.getElementById('runningTasks');
    const queuedTasks = document.getElementById('queuedTasks');
    const completedTasks = document.getElementById('completedTasks');
    
    // 初始化变量
    let currentTaskId = null;
    let currentFileId = null;
    let taskStatusInterval = null;
    let isBatchMode = false;
    let batchFiles = {
        textFiles: [],
        imageFiles: []
    };
    
    // 批量模式切换
    toggleBatchMode.addEventListener('click', function(e) {
        e.preventDefault();
        isBatchMode = !isBatchMode;
        batchOptionsSection.style.display = isBatchMode ? 'block' : 'none';
        // 单个任务模式下的语音选择和图片上传
        singleModeImageUpload.style.display = isBatchMode ? 'none' : 'block';
        
        if (isBatchMode) {
            textInput.disabled = true;
            textInput.placeholder = "批量模式下不需要在此输入文本";
            textInput.value = "";
            toggleBatchMode.innerHTML = '<i class="bi bi-file-text"></i> 单文件模式';
        } else {
            textInput.disabled = false;
            textInput.placeholder = "请输入要转换为视频的文本...";
            toggleBatchMode.innerHTML = '<i class="bi bi-folder"></i> 批量文件夹模式';
            fileList.innerHTML = '';
            batchFiles = { textFiles: [], imageFiles: [] };
            folderInput.value = '';
        }
    });
    
    // 监听文件夹选择
    folderInput.addEventListener('change', function(e) {
        const files = e.target.files;
        if (!files || files.length === 0) return;
        
        // 重置文件列表
        batchFiles = {
            textFiles: [],
            imageFiles: []
        };
        
        // 处理文件
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const fileName = file.name.toLowerCase();
            const fileNameWithoutExt = fileName.split('.')[0];
            
            if (fileName.endsWith('.txt')) {
                batchFiles.textFiles.push({
                    file: file,
                    name: fileNameWithoutExt,
                    paired: false
                });
            } else if (fileName.endsWith('.jpg') || fileName.endsWith('.jpeg') || fileName.endsWith('.png')) {
                batchFiles.imageFiles.push({
                    file: file,
                    name: fileNameWithoutExt,
                    paired: false
                });
            }
        }
        
        // 显示文件配对信息
        displayFileList();
    });
    
    // 显示文件配对列表
    function displayFileList() {
        if (!batchFiles.textFiles.length) {
            fileList.innerHTML = '<div class="alert alert-warning my-2">未找到任何文本文件(.txt)</div>';
            return;
        }
        
        // 配对文件
        let pairedCount = 0;
        let totalFiles = batchFiles.textFiles.length;
        let listHtml = '<div class="list-group">';
        
        // 检查每个文本文件是否有匹配的图片
        batchFiles.textFiles.forEach(textFile => {
            const matchingImage = batchFiles.imageFiles.find(imgFile => imgFile.name === textFile.name);
            if (matchingImage) {
                textFile.paired = true;
                matchingImage.paired = true;
                pairedCount++;
            }
            
            listHtml += `
                <div class="list-group-item p-2">
                    <div class="d-flex align-items-center">
                        <div>
                            <i class="bi bi-file-text text-primary me-2"></i>${textFile.file.name}
                        </div>
                        <div class="ms-auto">
                            ${matchingImage 
                                ? '<span class="badge bg-success"><i class="bi bi-check"></i> 已配对图片</span>' 
                                : '<span class="badge bg-secondary"><i class="bi bi-exclamation-triangle"></i> 无配对图片</span>'}
                        </div>
                    </div>
                </div>
            `;
        });
        
        listHtml += '</div>';
        
        // 添加统计信息
        listHtml = `
            <div class="alert alert-info mb-2">
                找到 ${totalFiles} 个文本文件，${pairedCount} 个有配对图片
            </div>
            ${listHtml}
        `;
        
        fileList.innerHTML = listHtml;
    }
    
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
    
    // 处理文本分割
    function splitText(text) {
        const result = [];
        const maxLength = parseInt(maxTextLength.value) || 500;
        
        if (!isBatchMode) {
            return [text]; // 非批量模式，直接返回原文本
        }
        
        let segments = [];
        
        // 按段落分割
        if (splitByParagraph.checked) {
            segments = text.split(/\n\s*\n/).filter(s => s.trim().length > 0);
        } else {
            segments = [text];
        }
        
        // 按句子分割（如果选择了该选项）
        if (splitBySentence.checked) {
            const sentenceSegments = [];
            segments.forEach(segment => {
                // 按中文或英文句号、问号、感叹号分割
                const sentences = segment.split(/(?<=[。？！.?!])\s*/).filter(s => s.trim().length > 0);
                sentenceSegments.push(...sentences);
            });
            segments = sentenceSegments;
        }
        
        // 处理长度限制
        for (let segment of segments) {
            if (segment.length <= maxLength) {
                result.push(segment);
            } else {
                // 超长文本按字符数分割
                let i = 0;
                while (i < segment.length) {
                    result.push(segment.substring(i, i + maxLength));
                    i += maxLength;
                }
            }
        }
        
        return result;
    }
    
    // 提交单个任务（文本+可选图片）
    function submitTask(text, voice, imageFile) {
        return new Promise((resolve, reject) => {
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
                resolve(data.task_id);
            })
            .catch(error => {
                reject(error);
            });
        });
    }
    
    // 从文件中读取文本内容
    function readTextFile(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => resolve(e.target.result);
            reader.onerror = (e) => reject(new Error('读取文件失败'));
            reader.readAsText(file);
        });
    }
    
    // 处理表单提交
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const voice = voiceSelect.value;
        
        if (!voice) {
            showError('请选择语音');
            return;
        }
        
        // 禁用生成按钮
        generateBtn.disabled = true;
        
        try {
            if (isBatchMode) {
                // 批量模式处理
                if (!batchFiles.textFiles.length) {
                    throw new Error('请先选择包含文本文件的文件夹');
                }
                
                showMessage(`准备提交 ${batchFiles.textFiles.length} 个批量任务...`);
                
                // 逐个提交任务
                let successCount = 0;
                let failCount = 0;
                
                for (let i = 0; i < batchFiles.textFiles.length; i++) {
                    const textFileData = batchFiles.textFiles[i];
                    
                    try {
                        // 读取文本内容
                        const textContent = await readTextFile(textFileData.file);
                        
                        // 查找配对的图片
                        let imageFile = null;
                        const matchingImage = batchFiles.imageFiles.find(img => img.name === textFileData.name);
                        if (matchingImage) {
                            imageFile = matchingImage.file;
                        }
                        
                        // 提交任务
                        await submitTask(textContent, voice, imageFile);
                        successCount++;
                        showMessage(`已提交 ${i+1}/${batchFiles.textFiles.length} 个任务`);
                    } catch (error) {
                        console.error(`提交第 ${i+1} 个任务出错:`, error);
                        failCount++;
                        // 继续提交其他任务
                    }
                }
                
                if (successCount > 0) {
                    showMessage(`成功提交了 ${successCount} 个任务，${failCount > 0 ? failCount + ' 个失败' : ''}，请在任务列表中查看进度`);
                } else {
                    throw new Error('所有任务提交失败');
                }
                
            } else {
                // 单文件模式
                const text = textInput.value.trim();
                const imageFile = document.getElementById('imageInput').files[0];
                
                if (!text) {
                    throw new Error('请输入要转换的文本');
                }
                
                // 显示任务卡片
                taskCard.style.display = 'block';
                progressBar.style.width = '0%';
                taskMessage.textContent = '准备中...';
                downloadSection.style.display = 'none';
                
                // 提交任务
                currentTaskId = await submitTask(text, voice, imageFile);
                pollTaskStatus();
            }
            
            // 重置表单（单文件模式）
            if (!isBatchMode) {
                textInput.value = '';
                document.getElementById('imageInput').value = '';
            }
            
            generateBtn.disabled = false;
            
            // 刷新任务列表
            refreshTaskList();
            
        } catch (error) {
            showError(error.message);
            generateBtn.disabled = false;
        }
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
    
    // 显示消息通知
    function showMessage(message) {
        // 创建一个toast通知
        const toastContainer = document.querySelector('.toast-container');
        const toastElement = document.createElement('div');
        toastElement.className = 'toast';
        toastElement.setAttribute('role', 'alert');
        toastElement.setAttribute('aria-live', 'assertive');
        toastElement.setAttribute('aria-atomic', 'true');
        
        toastElement.innerHTML = `
            <div class="toast-header bg-success text-white">
                <strong class="me-auto"><i class="bi bi-info-circle"></i> 提示</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">${message}</div>
        `;
        
        toastContainer.appendChild(toastElement);
        
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
        
        // 5秒后自动移除
        setTimeout(() => {
            toastElement.remove();
        }, 5000);
    }
    
    // 初始化
    loadVoices();
    refreshTaskList();
    
    // 定期刷新任务列表
    setInterval(refreshTaskList, 5000);
}); 