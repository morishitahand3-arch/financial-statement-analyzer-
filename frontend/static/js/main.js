// ファイルアップロード処理
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const uploadProgress = document.getElementById('uploadProgress');
const progressBar = document.getElementById('progressBar');
const message = document.getElementById('message');

let selectedFile = null;

// ドラッグ＆ドロップ
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// ファイル選択
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// ファイル処理
function handleFileSelect(file) {
    if (!file.name.toLowerCase().endsWith('.pdf')) {
        showMessage('PDFファイルを選択してください', 'error');
        return;
    }

    if (file.size > 10 * 1024 * 1024) {
        showMessage('ファイルサイズは10MB以下にしてください', 'error');
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.style.display = 'block';
    uploadBtn.style.display = 'block';
    message.textContent = '';
}

// ファイルサイズをフォーマット
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// アップロード実行
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        showMessage('ファイルを選択してください', 'error');
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    uploadBtn.disabled = true;
    uploadProgress.style.display = 'block';
    progressBar.style.width = '0%';

    try {
        // プログレスバーをアニメーション
        progressBar.style.width = '50%';

        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        progressBar.style.width = '100%';

        const data = await response.json();

        if (response.ok) {
            showMessage('アップロード成功！分析結果ページに移動します...', 'success');
            setTimeout(() => {
                window.location.href = '/results?file=' + data.filename;
            }, 1500);
        } else {
            showMessage(data.error || 'アップロードに失敗しました', 'error');
            uploadBtn.disabled = false;
        }
    } catch (error) {
        showMessage('通信エラーが発生しました: ' + error.message, 'error');
        uploadBtn.disabled = false;
    }
});

// メッセージ表示
function showMessage(text, type) {
    message.textContent = text;
    message.className = 'message ' + type;
    message.style.display = 'block';
}
