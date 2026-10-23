import os
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eden_cloud_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

clipboard_history = []
CURRENT_CLIPBOARD = "Bienvenue sur ClipBoard Sync Cloud !"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ClipBoard Sync | EDEN DRC GROUP</title>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
            --card-bg: rgba(22, 27, 34, 0.75);
            --accent-blue: #2f81f7;
            --accent-hover: #58a6ff;
            --accent-orange: #f0883e;
            --success: #238636;
            --danger: #da3633;
            --text-main: #f0f6fc;
            --text-muted: #8b949e;
            --border: rgba(240, 246, 252, 0.1);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', sans-serif; }
        
        body {
            background: var(--bg-gradient);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 650px;
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 28px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
            animation: fadeIn 0.6s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(15px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }

        .brand-title {
            font-size: 1.4rem;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
            color: #ffffff;
        }

        .brand-badge {
            background: linear-gradient(45deg, var(--accent-orange), #f39c12);
            color: #000;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 6px;
            letter-spacing: 0.5px;
        }

        .status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.85rem;
            color: #3fb950;
            background: rgba(63, 185, 80, 0.1);
            padding: 6px 12px;
            border-radius: 20px;
            border: 1px solid rgba(63, 185, 80, 0.2);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #3fb950;
            border-radius: 50%;
            box-shadow: 0 0 8px #3fb950;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.4; transform: scale(1.2); }
            100% { opacity: 1; transform: scale(1); }
        }

        .welcome-msg {
            font-size: 0.95rem;
            color: var(--text-muted);
            margin-bottom: 18px;
        }

        .textarea-box {
            position: relative;
            margin-bottom: 20px;
        }

        textarea {
            width: 100%;
            height: 160px;
            background: rgba(13, 17, 23, 0.8);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 16px;
            color: var(--text-main);
            font-size: 1rem;
            resize: none;
            outline: none;
            transition: all 0.3s ease;
        }

        textarea:focus {
            border-color: var(--accent-blue);
            box-shadow: 0 0 12px rgba(47, 129, 247, 0.25);
        }

        .actions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 10px;
            margin-bottom: 24px;
        }

        .btn {
            border: none;
            padding: 12px 16px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            transition: all 0.2s ease;
        }

        .btn:active { transform: scale(0.97); }

        .btn-primary { background: var(--accent-blue); color: white; }
        .btn-primary:hover { background: var(--accent-hover); box-shadow: 0 4px 12px rgba(47, 129, 247, 0.3); }

        .btn-secondary { background: #21262d; color: var(--text-main); border: 1px solid var(--border); }
        .btn-secondary:hover { background: #30363d; color: white; }

        .btn-danger { background: rgba(218, 54, 51, 0.15); color: #f85149; border: 1px solid rgba(218, 54, 51, 0.3); }
        .btn-danger:hover { background: var(--danger); color: white; }

        .history-section {
            background: rgba(13, 17, 23, 0.4);
            border-radius: 12px;
            padding: 16px;
            border: 1px solid var(--border);
        }

        .history-title {
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .history-list {
            display: flex;
            flex-direction: column;
            gap: 8px;
            max-height: 140px;
            overflow-y: auto;
        }

        .history-item {
            background: rgba(22, 27, 34, 0.8);
            padding: 10px 14px;
            border-radius: 8px;
            font-size: 0.88rem;
            color: #c9d1d9;
            border: 1px solid var(--border);
            cursor: pointer;
            transition: background 0.2s;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }

        .history-item:hover { background: #21262d; color: var(--accent-hover); }

        .toast {
            position: fixed;
            bottom: 24px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: var(--success);
            color: white;
            padding: 10px 20px;
            border-radius: 30px;
            font-weight: 600;
            font-size: 0.9rem;
            box-shadow: 0 10px 20px rgba(0,0,0,0.4);
            opacity: 0;
            transition: all 0.3s ease;
            pointer-events: none;
        }

        .toast.show {
            transform: translateX(-50%) translateY(0);
            opacity: 1;
        }
    </style>
</head>
<body>

    <div class="container">
        <!-- En-tête / Header -->
        <div class="header">
            <div class="brand-title">
                <i class="fa-solid fa-paste" style="color: var(--accent-blue);"></i>
                ClipBoard Sync
                <span class="brand-badge">EDG</span>
            </div>
            <div class="status">
                <span class="status-dot"></span>
                <span>En ligne</span>
            </div>
        </div>

        <!-- Message de Salutation -->
        <div class="welcome-msg">
            👋 Bonjour ! Partagez vos textes et liens en temps réel sur tous vos appareils.
        </div>

        <!-- Zone de texte principal -->
        <div class="textarea-box">
            <textarea id="clipboard" placeholder="Tapez ou collez votre texte ici..."></textarea>
        </div>

        <!-- Grille de boutons d'action -->
        <div class="actions-grid">
            <button class="btn btn-primary" onclick="sendClipboard()">
                <i class="fa-solid fa-paper-plane"></i> Mettre à jour
            </button>
            <button class="btn btn-secondary" onclick="copyToClipboard()">
                <i class="fa-solid fa-copy"></i> Copier
            </button>
            <button class="btn btn-danger" onclick="clearClipboard()">
                <i class="fa-solid fa-trash-can"></i> Effacer
            </button>
        </div>

        <!-- Historique Récent -->
        <div class="history-section">
            <div class="history-title">
                <i class="fa-solid fa-clock-rotate-left"></i> Historique récent
            </div>
            <div class="history-list" id="historyList">
                <div class="history-item" style="color: var(--text-muted); text-align: center;">Aucun élément récent</div>
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div id="toast" class="toast">
        <i class="fa-solid fa-circle-check"></i> <span id="toastMsg">Copié dans le presse-papiers !</span>
    </div>

    <script>
        const socket = io();
        const textarea = document.getElementById('clipboard');
        const historyList = document.getElementById('historyList');

        socket.on('connect', () => {
            console.log('Connecté au serveur Cloud EDG');
        });

        socket.on('update_clipboard', (data) => {
            textarea.value = data.text;
            updateHistory(data.history);
        });

        function sendClipboard() {
            const text = textarea.value;
            socket.emit('sync_text', { text: text });
            showToast('Presse-papiers synchronisé !');
        }

        function copyToClipboard() {
            if (!textarea.value) return;
            navigator.clipboard.writeText(textarea.value).then(() => {
                showToast('Texte copié !');
            });
        }

        function clearClipboard() {
            textarea.value = '';
            socket.emit('sync_text', { text: '' });
            showToast('Presse-papiers effacé !');
        }

        function updateHistory(history) {
            if (!history || history.length === 0) return;
            historyList.innerHTML = '';
            history.slice(-5).reverse().forEach(item => {
                const div = document.createElement('div');
                div.className = 'history-item';
                div.innerText = item;
                div.onclick = () => {
                    textarea.value = item;
                    sendClipboard();
                };
                historyList.appendChild(div);
            });
        }

        function showToast(message) {
            const toast = document.getElementById('toast');
            document.getElementById('toastMsg').innerText = message;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2500);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@socketio.on('sync_text')
def handle_sync(data):
    global CURRENT_CLIPBOARD, clipboard_history
    text = data.get('text', '')
    CURRENT_CLIPBOARD = text
    if text and (not clipboard_history or clipboard_history[-1] != text):
        clipboard_history.append(text)
        if len(clipboard_history) > 10:
            clipboard_history.pop(0)
    emit('update_clipboard', {'text': CURRENT_CLIPBOARD, 'history': clipboard_history}, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)