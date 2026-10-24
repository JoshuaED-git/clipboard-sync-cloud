import os
from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eden_cloud_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

clipboard_history = []
CURRENT_CLIPBOARD = "Bienvenue sur ClipBoard Sync Cloud !"
MEMO_CONTENT = ""

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
            --card-bg: rgba(22, 27, 34, 0.85);
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
            overflow: hidden;
        }

        /* --- SPLASH SCREEN ANIMATION --- */
        #splash-screen {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: #090d16;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            transition: opacity 0.8s ease, visibility 0.8s ease;
        }

        .splash-logo {
            font-size: 4rem;
            color: white;
            background: linear-gradient(135deg, #1f6feb, var(--accent-orange));
            width: 100px; height: 100px;
            display: flex; align-items: center; justify-content: center;
            border-radius: 20px;
            box-shadow: 0 10px 30px rgba(47, 129, 247, 0.4);
            animation: dropBounce 1.2s cubic-bezier(0.25, 1, 0.5, 1) forwards;
        }

        @keyframes dropBounce {
            0% { transform: translateY(-150px) scale(0.5); opacity: 0; }
            60% { transform: translateY(20px) scale(1.05); opacity: 1; }
            80% { transform: translateY(-10px) scale(0.95); }
            100% { transform: translateY(0) scale(1); opacity: 1; }
        }

        .splash-text {
            margin-top: 20px;
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--text-muted);
            border-right: 2px solid var(--accent-blue);
            white-space: nowrap;
            overflow: hidden;
            width: 0;
            animation: typing 2s steps(25, end) 0.8s forwards, blink 0.75s step-end infinite;
        }

        @keyframes typing { from { width: 0; } to { width: 280px; } }
        @keyframes blink { from, to { border-color: transparent; } 50% { border-color: var(--accent-blue); } }

        /* --- MAIN APP CONTAINER --- */
        .container {
            width: 100%;
            max-width: 650px;
            background: var(--card-bg);
            backdrop-filter: blur(16px);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 28px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6);
            opacity: 0;
            transform: translateY(20px);
            transition: all 0.8s ease 0.3s;
        }

        .container.visible {
            opacity: 1;
            transform: translateY(0);
        }

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
            padding-bottom: 14px;
            border-bottom: 1px solid var(--border);
        }

        .brand-title {
            font-size: 1.3rem;
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
        }

        .status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 0.82rem;
            color: #3fb950;
            background: rgba(63, 185, 80, 0.1);
            padding: 5px 12px;
            border-radius: 20px;
            border: 1px solid rgba(63, 185, 80, 0.2);
        }

        .status-dot {
            width: 7px; height: 7px;
            background-color: #3fb950;
            border-radius: 50%;
            box-shadow: 0 0 8px #3fb950;
            animation: pulse 2s infinite;
        }

        @keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(1.2); } 100% { opacity: 1; transform: scale(1); } }

        /* Salutation dynamique */
        .welcome-msg {
            font-size: 1rem;
            font-weight: 600;
            color: var(--accent-hover);
            margin-bottom: 16px;
            background: rgba(47, 129, 247, 0.08);
            padding: 10px 14px;
            border-radius: 10px;
            border-left: 3px solid var(--accent-blue);
        }

        .textarea-box { position: relative; margin-bottom: 16px; }

        textarea {
            width: 100%;
            height: 130px;
            background: rgba(13, 17, 23, 0.8);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px;
            color: var(--text-main);
            font-size: 0.95rem;
            resize: none;
            outline: none;
            transition: all 0.3s ease;
        }

        textarea:focus { border-color: var(--accent-blue); box-shadow: 0 0 10px rgba(47, 129, 247, 0.25); }

        .actions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 10px;
            margin-bottom: 20px;
        }

        .btn {
            border: none;
            padding: 11px 14px;
            border-radius: 10px;
            font-weight: 600;
            font-size: 0.88rem;
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
        .btn-memo { background: rgba(240, 136, 62, 0.15); color: var(--accent-orange); border: 1px solid rgba(240, 136, 62, 0.3); }
        .btn-memo:hover { background: var(--accent-orange); color: white; }

        /* Bloc Mémo escamotable (+) */
        .memo-container {
            display: none;
            margin-bottom: 16px;
            animation: fadeIn 0.3s ease;
        }
        .memo-container.active { display: block; }
        .memo-textarea { height: 80px; font-size: 0.88rem; margin-top: 6px; }

        .history-section {
            background: rgba(13, 17, 23, 0.4);
            border-radius: 12px;
            padding: 14px;
            border: 1px solid var(--border);
        }

        .history-title {
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .history-list {
            display: flex;
            flex-direction: column;
            gap: 6px;
            max-height: 110px;
            overflow-y: auto;
        }

        .history-item {
            background: rgba(22, 27, 34, 0.8);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.84rem;
            color: #c9d1d9;
            border: 1px solid var(--border);
            cursor: pointer;
            transition: background 0.2s;
            white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
        }

        .history-item:hover { background: #21262d; color: var(--accent-hover); }

        /* Modal Onboarding (Premier nom) */
        #onboard-modal {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8);
            display: none; justify-content: center; align-items: center;
            z-index: 10000;
            backdrop-filter: blur(8px);
        }
        .modal-box {
            background: #161b22; border: 1px solid var(--border); padding: 24px;
            border-radius: 16px; width: 90%; max-width: 400px; text-align: center;
            box-shadow: 0 20px 40px rgba(0,0,0,0.8);
        }
        .modal-box h3 { margin-bottom: 12px; color: white; font-size: 1.2rem; }
        .modal-box p { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 16px; }
        .modal-box input {
            width: 100%; padding: 12px; background: #0d1117; border: 1px solid var(--border);
            border-radius: 8px; color: white; font-size: 1rem; margin-bottom: 16px; outline: none;
        }

        .toast {
            position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%) translateY(100px);
            background: var(--success); color: white; padding: 10px 20px; border-radius: 30px;
            font-weight: 600; font-size: 0.88rem; box-shadow: 0 10px 20px rgba(0,0,0,0.4);
            opacity: 0; transition: all 0.3s ease; pointer-events: none; z-index: 10001;
        }
        .toast.show { transform: translateX(-50%) translateY(0); opacity: 1; }
    </style>
</head>
<body>

    <!-- Splash Screen EDG -->
    <div id="splash-screen">
        <div class="splash-logo"><i class="fa-solid fa-paste"></i></div>
        <div class="splash-text">EDEN DRC GROUP - Sync...</div>
    </div>

    <!-- Modal d'accueil premier lancement -->
    <div id="onboard-modal">
        <div class="modal-box">
            <h3>Bienvenue sur ClipBoard Sync</h3>
            <p>Comment souhaitez-vous que EDG vous appelle ?</p>
            <input type="text" id="usernameInput" placeholder="Entrez votre prénom ou nom...">
            <button class="btn btn-primary" style="width: 100%;" onclick="saveUsername()">Commencer l'aventure</button>
        </div>
    </div>

    <div class="container" id="mainContainer">
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

        <!-- Salutation Aléatoire & Personnalisée -->
        <div class="welcome-msg" id="greetingMsg">
            👋 Chargement de vos salutations...
        </div>

        <div class="textarea-box">
            <textarea id="clipboard" placeholder="Tapez ou collez votre texte ici..."></textarea>
        </div>

        <!-- Bloc Mémo additionnel (+) -->
        <div class="memo-container" id="memoContainer">
            <div class="history-title" style="color: var(--accent-orange);"><i class="fa-solid fa-note-sticky"></i> Bloc-notes rapide synchronisé</div>
            <textarea id="memoBox" class="textarea memo-textarea" placeholder="Notez des idées rapides ici..." oninput="syncMemo()"></textarea>
        </div>

        <div class="actions-grid">
            <button class="btn btn-primary" onclick="sendClipboard()">
                <i class="fa-solid fa-paper-plane"></i> Mettre à jour
            </button>
            <button class="btn btn-secondary" onclick="copyToClipboard()">
                <i class="fa-solid fa-copy"></i> Copier
            </button>
            <button class="btn btn-memo" onclick="toggleMemo()">
                <i class="fa-solid fa-plus"></i> Mémo (+)
            </button>
            <button class="btn btn-danger" onclick="clearClipboard()">
                <i class="fa-solid fa-trash-can"></i> Effacer
            </button>
        </div>

        <div class="history-section">
            <div class="history-title">
                <i class="fa-solid fa-clock-rotate-left"></i> Historique récent
            </div>
            <div class="history-list" id="historyList">
                <div class="history-item" style="color: var(--text-muted); text-align: center;">Aucun élément récent</div>
            </div>
        </div>
    </div>

    <div id="toast" class="toast">
        <i class="fa-solid fa-circle-check"></i> <span id="toastMsg">Action réussie !</span>
    </div>

    <script>
        const socket = io();
        const textarea = document.getElementById('clipboard');
        const memoBox = document.getElementById('memoBox');
        const historyList = document.getElementById('historyList');

        // Gestion du nom d'utilisateur et salutations aléatoires
        const greetings = [
            "Prêt à propulser tes projets aujourd'hui",
            "La puissance d'EDG à portée de main",
            "Heureux de te revoir en forme",
            "Tes idées n'attendent que d'être partagées",
            "Que vas-tu synchroniser de beau aujourd'hui",
            "L'excellence technique commence ici"
        ];

        window.addEventListener('DOMContentLoaded', () => {
            let username = localStorage.getItem('edg_username');
            if (!username) {
                document.getElementById('onboard-modal').style.display = 'flex';
            } else {
                initGreeting(username);
            }

            // Disparition du Splash Screen après l'animation
            setTimeout(() => {
                document.getElementById('splash-screen').style.opacity = '0';
                setTimeout(() => {
                    document.getElementById('splash-screen').style.display = 'none';
                    document.getElementById('mainContainer').classList.add('visible');
                }, 800);
            }, 2200);
        });

        function saveUsername() {
            const val = document.getElementById('usernameInput').value.trim();
            if (val) {
                localStorage.setItem('edg_username', val);
                document.getElementById('onboard-modal').style.display = 'none';
                initGreeting(val);
                document.getElementById('mainContainer').classList.add('visible');
            }
        }

        function initGreeting(name) {
            const randomText = greetings[Math.floor(Math.random() * greetings.length)];
            document.getElementById('greetingMsg').innerText = `👋 Salut ${name} ! ${randomText}.`;
        }

        function toggleMemo() {
            const box = document.getElementById('memoContainer');
            box.classList.toggle('active');
        }

        socket.on('connect', () => {
            console.log('Connecté au serveur Cloud EDG');
        });

        socket.on('update_clipboard', (data) => {
            textarea.value = data.text;
            if (data.memo !== undefined && memoBox.value !== data.memo) {
                memoBox.value = data.memo;
            }
            updateHistory(data.history);
        });

        function sendClipboard() {
            socket.emit('sync_text', { text: textarea.value, memo: memoBox.value });
            showToast('Presse-papiers synchronisé !');
        }

        function syncMemo() {
            socket.emit('sync_text', { text: textarea.value, memo: memoBox.value });
        }

        function copyToClipboard() {
            if (!textarea.value) return;
            navigator.clipboard.writeText(textarea.value).then(() => {
                showToast('Texte copié !');
            });
        }

        function clearClipboard() {
            textarea.value = '';
            socket.emit('sync_text', { text: '', memo: memoBox.value });
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
    global CURRENT_CLIPBOARD, MEMO_CONTENT, clipboard_history
    text = data.get('text', '')
    memo = data.get('memo', '')
    
    CURRENT_CLIPBOARD = text
    MEMO_CONTENT = memo
    
    if text and (not clipboard_history or clipboard_history[-1] != text):
        clipboard_history.append(text)
        if len(clipboard_history) > 10:
            clipboard_history.pop(0)
            
    emit('update_clipboard', {
        'text': CURRENT_CLIPBOARD, 
        'memo': MEMO_CONTENT, 
        'history': clipboard_history
    }, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)