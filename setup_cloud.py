import os
print("🚀 Initialisation de ClipBoard Sync Cloud...")
# 1. Création du fichier app.py (Le serveur Flask)
app_code = '''from flask import Flask, render_template_string, request, jsonify
app = Flask(__name__)
app.config['SECRET_KEY'] = 'eden_cloud_secret'
clipboard_history = []
CURRENT_CLIPBOARD = "Bienvenue sur ClipBoard Sync Cloud ! Accessible 24h/24."
HTML_TEMPLATE = \"\"\"
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>ClipBoard Sync Cloud</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --card-bg: #1e293b;
            --text-color: #f8fafc;
            --text-muted: #94a3b8;
            --primary: #38bdf8;
            --primary-hover: #0ea5e9;
            --danger: #f43f5e;
            --success: #22c55e;
            --border: #334155;
        }
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 16px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            box-sizing: border-box;
        }
        .app-container {
            width: 100%;
            max-width: 500px;
            background: var(--card-bg);
            border-radius: 16px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            border: 1px solid var(--border);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .app-header {
            padding: 16px 20px;
            background: rgba(15, 23, 42, 0.5);
            border-bottom: 1px solid var(--border);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .app-title { font-size: 18px; font-weight: 700; color: var(--primary); margin: 0; }
        .status-badge {
            font-size: 12px; padding: 4px 10px; border-radius: 20px;
            background: rgba(34, 197, 94, 0.15); color: var(--success); font-weight: 600;
            display: flex; align-items: center; gap: 6px;
        }
        .status-dot { width: 8px; height: 8px; background-color: var(--success); border-radius: 50%; }
        .app-body { padding: 20px; display: flex; flex-direction: column; gap: 16px; }
        label { font-size: 13px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; }
        textarea {
            width: 100%; height: 130px; background: #0f172a; border: 1px solid var(--border);
            border-radius: 10px; padding: 12px; color: var(--text-color); font-size: 15px;
            box-sizing: border-box; resize: none; outline: none;
        }
        textarea:focus { border-color: var(--primary); }
        .action-row { display: flex; gap: 10px; }
        button {
            flex: 1; padding: 12px; border-radius: 10px; font-size: 14px; font-weight: 600;
            border: none; cursor: pointer; transition: background 0.2s;
        }
        .btn-primary { background-color: var(--primary); color: #0f172a; }
        .btn-primary:hover { background-color: var(--primary-hover); }
        .btn-danger { background-color: rgba(244, 63, 94, 0.15); color: var(--danger); }
        .btn-danger:hover { background-color: var(--danger); color: white; }
        .history-container { margin-top: 10px; border-top: 1px solid var(--border); padding-top: 16px; }
        .history-list { max-height: 200px; overflow-y: auto; display: flex; flex-direction: column; gap: 8px; }
        .history-item {
            background: #0f172a; border: 1px solid var(--border); padding: 10px 12px;
            border-radius: 8px; display: flex; justify-content: space-between; align-items: center; gap: 10px;
        }
        .history-text { font-size: 13px; color: var(--text-muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1; }
        .btn-sm { padding: 6px 10px; font-size: 12px; border-radius: 6px; background: var(--border); color: var(--text-color); flex: unset; }
        .btn-sm:hover { background: var(--primary); color: #0f172a; }
        .toast {
            position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%) translateY(100px);
            background: var(--success); color: #0f172a; padding: 10px 20px; border-radius: 30px;
            font-weight: 600; font-size: 13px; transition: transform 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .toast.show { transform: translateX(-50%) translateY(0); }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="app-header">
            <h1 class="app-title">📋 ClipBoard Cloud</h1>
            <div class="status-badge"><div class="status-dot"></div> En ligne</div>
        </div>
        <div class="app-body">
            <div>
                <label>Presse-papiers Actuel</label>
                <textarea id="clipText" placeholder="Tape ou colle ton texte ici..."></textarea>
            </div>
            <div class="action-row">
                <button class="btn-primary" onclick="updateClipboard()">Mettre à jour</button>
                <button class="btn-danger" onclick="clearHistory()">Tout effacer</button>
            </div>
            <div class="history-container">
                <label>Historique distant</label>
                <div id="historyList" class="history-list"></div>
            </div>
        </div>
    </div>
    <div id="toast" class="toast">Synchronisé !</div>
    <script>
        const clipText = document.getElementById('clipText');
        const historyList = document.getElementById('historyList');
        const toast = document.getElementById('toast');
        function showToast(msg) {
            toast.textContent = msg;
            toast.classList.add('show');
            setTimeout(() => toast.classList.remove('show'), 2000);
        }
        async function fetchState() {
            try {
                let res = await fetch('/api/get');
                let data = await res.json();
                if (document.activeElement !== clipText) {
                    clipText.value = data.current;
                }
                renderHistory(data.history);
            } catch (e) { console.error(e); }
        }
        async function updateClipboard() {
            let text = clipText.value;
            await fetch('/api/set', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: text})
            });
            showToast("Texte envoyé au cloud !");
            fetchState();
        }
        async function clearHistory() {
            await fetch('/api/clear', {method: 'POST'});
            showToast("Historique vidé");
            fetchState();
        }
        function copyText(text) {
            navigator.clipboard.writeText(text).then(() => showToast("Copié !"));
        }
        function renderHistory(history) {
            historyList.innerHTML = '';
            if (history.length === 0) {
                historyList.innerHTML = '<div style="color: var(--text-muted); text-align: center; font-size: 13px; padding: 15px;">Aucun historique</div>';
                return;
            }
            history.forEach(item => {
                let div = document.createElement('div');
                div.className = 'history-item';
                div.innerHTML = `<span class="history-text">${escapeHtml(item)}</span>
                                 <button class="btn-sm" onclick="copyText(` + "`" + escapeJs(item) + "`" + `)">Copier</button>`;
                historyList.appendChild(div);
            });
        }
        function escapeHtml(t) { return t.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
        function escapeJs(t) { return t.replace(/\\/g, '\\\\').replace(/`/g, '\\`'); }
        setInterval(fetchState, 2000);
        fetchState();
    </script>
</body>
</html>
\"\"\"
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)
@app.route('/api/get', methods=['GET'])
def get_clipboard():
    return jsonify({'current': CURRENT_CLIPBOARD, 'history': clipboard_history})
@app.route('/api/set', methods=['POST'])
def set_clipboard():
    global CURRENT_CLIPBOARD
    data = request.get_json()
    text = data.get('text', '')
    if text and text != CURRENT_CLIPBOARD:
        CURRENT_CLIPBOARD = text
        if not clipboard_history or clipboard_history[0] != text:
            clipboard_history.insert(0, text)
            if len(clipboard_history) > 50:
                clipboard_history.pop()
    return jsonify({'status': 'success'})
@app.route('/api/clear', methods=['POST'])
def clear_clipboard():
    global clipboard_history, CURRENT_CLIPBOARD
    clipboard_history = []
    CURRENT_CLIPBOARD = ""
    return jsonify({'status': 'success'})
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
'''
with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)
print(" -> Fichier 'app.py' généré avec succès.")
# 2. Création du fichier requirements.txt
with open("requirements.txt", "w", encoding="utf-8") as f:
    f.write("flask\ngunicorn\n")
print(" -> Fichier 'requirements.txt' généré.")
# 3. Création du fichier Procfile
with open("Procfile", "w", encoding="utf-8") as f:
    f.write("web: gunicorn app:app\n")
print(" -> Fichier 'Procfile' généré.")
print("\n✨ Tout est prêt et configuré à la bonne place ! Tu peux maintenant pousser sur GitHub pour le cloud.")