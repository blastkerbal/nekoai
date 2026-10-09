#!/usr/bin/env python3
"""
🐾 NekoText Web GUI 🐾
A cute local browser interface for Anime Catgirl Mode conversion.
Zero external dependencies - runs on Python's built-in http.server!
"""

import sys
import os
import json
import webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import parse_qs, urlparse

# Import logic from catgirl.py
from catgirl import (
    load_config,
    save_config,
    convert_to_catgirl,
    PERSONA_PROMPTS,
    CONFIG_FILE
)

PORT = 7860

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>🐾 NekoText - Anime Catgirl Converter</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600;700&family=Nunito:wght@400;600;800&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-color: #fff4f8;
      --card-bg: rgba(255, 255, 255, 0.92);
      --primary: #ff65a3;
      --primary-hover: #ff478f;
      --secondary: #9d65ff;
      --text: #4a3447;
      --text-muted: #8c7287;
      --border: #ffd1e4;
      --accent: #ffd166;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Nunito', sans-serif;
      background: linear-gradient(135deg, #fff0f5 0%, #ffe4ec 50%, #f3e8ff 100%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 24px 16px;
    }

    .container {
      width: 100%;
      max-width: 760px;
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      border-radius: 28px;
      border: 3px solid var(--border);
      box-shadow: 0 16px 40px rgba(255, 101, 163, 0.15);
      padding: 32px;
      margin-bottom: 24px;
    }

    header {
      text-align: center;
      margin-bottom: 24px;
    }

    .header-icon {
      font-size: 52px;
      display: inline-block;
      animation: float 3s ease-in-out infinite;
      cursor: pointer;
    }

    @keyframes float {
      0%, 100% { transform: translateY(0) rotate(0deg); }
      50% { transform: translateY(-8px) rotate(4deg); }
    }

    h1 {
      font-family: 'Fredoka', cursive;
      font-size: 32px;
      color: var(--primary);
      text-shadow: 2px 2px 0px #ffe0ed;
      margin-top: 8px;
    }

    .subtitle {
      font-size: 15px;
      color: var(--text-muted);
      margin-top: 4px;
    }

    /* Key status bar */
    .key-bar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background: #fff8fc;
      border: 1px dashed var(--border);
      border-radius: 14px;
      padding: 10px 16px;
      margin-bottom: 20px;
      font-size: 14px;
    }

    .key-status {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
    }

    .badge {
      display: inline-block;
      width: 10px;
      height: 10px;
      border-radius: 50%;
    }

    .badge-ok { background: #10b981; box-shadow: 0 0 8px #10b981; }
    .badge-missing { background: #ef4444; box-shadow: 0 0 8px #ef4444; }

    .btn-small {
      background: var(--secondary);
      color: white;
      border: none;
      padding: 6px 12px;
      border-radius: 10px;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s;
    }

    .btn-small:hover {
      opacity: 0.9;
      transform: scale(1.03);
    }

    /* Vibes selector */
    .section-title {
      font-family: 'Fredoka', cursive;
      font-size: 16px;
      color: var(--primary);
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .vibes-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
      gap: 10px;
      margin-bottom: 20px;
    }

    .vibe-card {
      border: 2px solid var(--border);
      border-radius: 16px;
      padding: 10px;
      text-align: center;
      cursor: pointer;
      background: white;
      transition: all 0.2s ease;
      user-select: none;
    }

    .vibe-card:hover {
      transform: translateY(-2px);
      border-color: var(--primary);
    }

    .vibe-card.active {
      border-color: var(--primary);
      background: #fff0f6;
      box-shadow: 0 4px 12px rgba(255, 101, 163, 0.25);
    }

    .vibe-emoji { font-size: 22px; }
    .vibe-name { font-weight: 800; font-size: 13px; color: var(--text); }
    .vibe-desc { font-size: 11px; color: var(--text-muted); margin-top: 2px; }

    /* Input area */
    .input-group {
      margin-bottom: 18px;
    }

    label {
      display: block;
      font-weight: 700;
      font-size: 14px;
      margin-bottom: 8px;
      color: var(--text);
    }

    textarea {
      width: 100%;
      height: 120px;
      border: 2px solid var(--border);
      border-radius: 18px;
      padding: 14px 16px;
      font-family: 'Nunito', sans-serif;
      font-size: 15px;
      color: var(--text);
      resize: vertical;
      background: #ffffff;
      outline: none;
      transition: border-color 0.2s;
    }

    textarea:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(255, 101, 163, 0.15);
    }

    /* Example presets */
    .presets {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      margin-top: 8px;
      align-items: center;
    }

    .presets-label {
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 600;
    }

    .preset-btn {
      background: #fbebf2;
      border: 1px solid #ffd8e8;
      border-radius: 8px;
      padding: 3px 8px;
      font-size: 11px;
      cursor: pointer;
      color: #9c3f6e;
      transition: all 0.15s;
    }

    .preset-btn:hover {
      background: var(--primary);
      color: white;
    }

    /* Convert Button */
    .action-btn {
      width: 100%;
      background: linear-gradient(135deg, var(--primary) 0%, #ff85b8 100%);
      color: white;
      border: none;
      border-radius: 18px;
      padding: 16px;
      font-family: 'Fredoka', cursive;
      font-size: 20px;
      font-weight: 700;
      cursor: pointer;
      box-shadow: 0 8px 20px rgba(255, 101, 163, 0.35);
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
    }

    .action-btn:hover:not(:disabled) {
      transform: translateY(-2px);
      box-shadow: 0 12px 24px rgba(255, 101, 163, 0.45);
    }

    .action-btn:active:not(:disabled) {
      transform: translateY(1px);
    }

    .action-btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    /* Output Card */
    .output-card {
      margin-top: 24px;
      display: none;
      animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .output-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 8px;
    }

    .output-box {
      background: #ffffff;
      border: 2px solid #ffd1e4;
      border-radius: 18px;
      padding: 18px 20px;
      font-size: 16px;
      line-height: 1.6;
      color: #3b2839;
      white-space: pre-wrap;
      word-break: break-word;
      position: relative;
    }

    .copy-btn {
      background: var(--primary);
      color: white;
      border: none;
      border-radius: 10px;
      padding: 6px 14px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.2s;
    }

    .copy-btn:hover {
      background: var(--primary-hover);
      transform: scale(1.05);
    }

    /* Modal for API Key */
    .modal-backdrop {
      display: none;
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0, 0, 0, 0.4);
      backdrop-filter: blur(4px);
      align-items: center;
      justify-content: center;
      z-index: 100;
    }

    .modal {
      background: white;
      border-radius: 24px;
      padding: 28px;
      width: 90%;
      max-width: 480px;
      border: 3px solid var(--border);
      box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }

    .modal h2 {
      font-family: 'Fredoka', cursive;
      color: var(--primary);
      margin-bottom: 12px;
    }

    .modal p {
      font-size: 14px;
      color: var(--text-muted);
      margin-bottom: 16px;
      line-height: 1.5;
    }

    .modal input {
      width: 100%;
      padding: 12px 14px;
      border: 2px solid var(--border);
      border-radius: 12px;
      font-size: 14px;
      margin-bottom: 16px;
      outline: none;
    }

    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }

    .btn-secondary {
      background: #e2e8f0;
      border: none;
      padding: 10px 18px;
      border-radius: 12px;
      font-weight: 700;
      cursor: pointer;
    }

    .footer {
      font-size: 13px;
      color: var(--text-muted);
      text-align: center;
    }
  </style>
</head>
<body>

  <div class="container">
    <header>
      <div class="header-icon" onclick="sparkle()">🐱✨</div>
      <h1>NekoText</h1>
      <p class="subtitle">Convert any boring text into authentic anime catgirl mode, nya~!</p>
    </header>

    <!-- Key status -->
    <div class="key-bar">
      <div class="key-status" id="key-status-text">
        <span class="badge" id="key-badge"></span>
        <span id="key-label">Checking API Key...</span>
      </div>
      <button class="btn-small" onclick="openKeyModal()">⚙️ Set API Key</button>
    </div>

    <!-- Vibe Selector -->
    <div class="section-title">✨ Pick a Catgirl Vibe</div>
    <div class="vibes-grid">
      <div class="vibe-card active" data-vibe="kawaii" onclick="selectVibe('kawaii')">
        <div class="vibe-emoji">🎀</div>
        <div class="vibe-name">Kawaii</div>
        <div class="vibe-desc">Sweet, cute, classic nya~</div>
      </div>
      <div class="vibe-card" data-vibe="tsundere" onclick="selectVibe('tsundere')">
        <div class="vibe-emoji">💢</div>
        <div class="vibe-name">Tsundere</div>
        <div class="vibe-desc">B-Baka! Don't look at me!</div>
      </div>
      <div class="vibe-card" data-vibe="hyper" onclick="selectVibe('hyper')">
        <div class="vibe-emoji">⚡</div>
        <div class="vibe-name">Hyper</div>
        <div class="vibe-desc">MAXIMUM ZOOMIES!!</div>
      </div>
      <div class="vibe-card" data-vibe="sleepy" onclick="selectVibe('sleepy')">
        <div class="vibe-emoji">💤</div>
        <div class="vibe-name">Sleepy</div>
        <div class="vibe-desc">Warm kotatsu cat nap</div>
      </div>
      <div class="vibe-card" data-vibe="villain" onclick="selectVibe('villain')">
        <div class="vibe-emoji">👑</div>
        <div class="vibe-name">Villainess</div>
        <div class="vibe-desc">Ohohoho~ foolish mortal!</div>
      </div>
    </div>

    <!-- Text Input -->
    <div class="input-group">
      <label for="input-text">🐾 Human Text:</label>
      <textarea id="input-text" placeholder="Type or paste your boring human message here..."></textarea>
      
      <div class="presets">
        <span class="presets-label">Quick test:</span>
        <button class="preset-btn" onclick="setPreset('Can you please email me the quarterly financial spreadsheet before Friday afternoon?')">💼 Work Email</button>
        <button class="preset-btn" onclick="setPreset('Error 500: Database connection timed out on line 42 of worker thread.')">💻 Code Bug</button>
        <button class="preset-btn" onclick="setPreset('I forgot my house keys inside again and now I am locked out in the cold rain.')">🌧️ Locked Out</button>
        <button class="preset-btn" onclick="setPreset('Hey, do you want to grab ramen and play video games tonight?')">🍜 Hangout</button>
      </div>
    </div>

    <!-- Convert Button -->
    <button class="action-btn" id="convert-btn" onclick="convertText()">
      <span id="btn-text">Nya-tify! ✨ (=^･ω･^=)</span>
    </button>

    <!-- Output Box -->
    <div class="output-card" id="output-container">
      <div class="output-header">
        <div class="section-title">ฅ(=^･ω･^=)ฅ Catgirl Translation:</div>
        <button class="copy-btn" id="copy-btn" onclick="copyOutput()">📋 Copy Nya!</button>
      </div>
      <div class="output-box" id="output-box"></div>
    </div>
  </div>

  <div class="footer">
    NekoText • Powered by Google Gemini API &bull; Mode: Local Host
  </div>

  <!-- API Key Modal -->
  <div class="modal-backdrop" id="key-modal">
    <div class="modal">
      <h2>🔑 Gemini API Key</h2>
      <p>Enter your Gemini API key below. It will be saved into your <code>config.json</code> file automatically.</p>
      <input type="password" id="api-key-input" placeholder="AIzaSy...">
      <div style="font-size: 12px; margin-bottom: 16px; color: #8c7287;">
        Need a key? Get one for free at <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color: var(--primary);">Google AI Studio</a>.
      </div>
      <div class="modal-actions">
        <button class="btn-secondary" onclick="closeKeyModal()">Cancel</button>
        <button class="copy-btn" onclick="saveKey()">Save Key</button>
      </div>
    </div>
  </div>

  <script>
    let currentVibe = 'kawaii';

    async function checkStatus() {
      try {
        const res = await fetch('/api/status');
        const data = await res.json();
        const badge = document.getElementById('key-badge');
        const label = document.getElementById('key-label');

        if (data.has_key) {
          badge.className = 'badge badge-ok';
          label.textContent = `API Key Active (${data.model})`;
        } else {
          badge.className = 'badge badge-missing';
          label.textContent = 'API Key Missing! Click to set';
        }
      } catch (e) {
        console.error(e);
      }
    }

    function selectVibe(vibe) {
      currentVibe = vibe;
      document.querySelectorAll('.vibe-card').forEach(c => {
        c.classList.toggle('active', c.dataset.vibe === vibe);
      });
    }

    function setPreset(text) {
      document.getElementById('input-text').value = text;
    }

    async function convertText() {
      const text = document.getElementById('input-text').value.trim();
      if (!text) {
        alert('Please enter some text to convert nya~!');
        return;
      }

      const btn = document.getElementById('convert-btn');
      const btnText = document.getElementById('btn-text');
      const outputCard = document.getElementById('output-container');
      const outputBox = document.getElementById('output-box');

      btn.disabled = true;
      btnText.textContent = 'Translating nya... 🐾✨';

      try {
        const res = await fetch('/api/convert', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: text, vibe: currentVibe })
        });
        const data = await res.json();

        if (data.error) {
          alert('Error: ' + data.error);
          if (data.error.includes('API key')) {
            openKeyModal();
          }
        } else {
          outputBox.textContent = data.result;
          outputCard.style.display = 'block';
          outputCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      } catch (err) {
        alert('Failed to connect to converter: ' + err);
      } finally {
        btn.disabled = false;
        btnText.textContent = 'Nya-tify! ✨ (=^･ω･^=)';
      }
    }

    async function copyOutput() {
      const outputBox = document.getElementById('output-box');
      const copyBtn = document.getElementById('copy-btn');
      try {
        await navigator.clipboard.writeText(outputBox.textContent);
        copyBtn.textContent = '✅ Copied!';
        setTimeout(() => copyBtn.textContent = '📋 Copy Nya!', 2000);
      } catch (e) {
        // Fallback via prompt
        alert('Copied output!');
      }
    }

    function openKeyModal() {
      document.getElementById('key-modal').style.display = 'flex';
      document.getElementById('api-key-input').focus();
    }

    function closeKeyModal() {
      document.getElementById('key-modal').style.display = 'none';
    }

    async function saveKey() {
      const key = document.getElementById('api-key-input').value.trim();
      if (!key) return;

      const res = await fetch('/api/key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ key: key })
      });
      const data = await res.json();
      if (data.success) {
        closeKeyModal();
        checkStatus();
        alert('✨ API Key saved successfully nya~!');
      }
    }

    function sparkle() {
      alert('Nyaaa~! (=^･ω･^=) Have a wonderful day!');
    }

    // Initialize
    checkStatus();
  </script>
</body>
</html>
"""

class CatgirlHTTPHandler(BaseHTTPRequestHandler):
    def _send_json(self, data: dict, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif parsed.path == "/api/status":
            config, _ = load_config()
            key = config.get("gemini_api_key", "").strip()
            env_key = os.environ.get("GEMINI_API_KEY", "").strip()
            has_key = bool((key and key != "YOUR_GEMINI_API_KEY_HERE") or env_key)
            self._send_json({
                "has_key": has_key,
                "model": config.get("model", "gemini-2.5-flash"),
                "vibe": config.get("default_vibe", "kawaii")
            })
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        parsed = urlparse(self.path)
        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len).decode("utf-8")

        try:
            payload = json.loads(post_body) if post_body else {}
        except Exception:
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        if parsed.path == "/api/convert":
            text = payload.get("text", "").strip()
            vibe = payload.get("vibe", "kawaii")

            if not text:
                self._send_json({"error": "No text provided"}, 400)
                return

            config, config_path = load_config()
            key = config.get("gemini_api_key", "").strip()
            env_key = os.environ.get("GEMINI_API_KEY", "").strip()
            api_key = key if (key and key != "YOUR_GEMINI_API_KEY_HERE") else env_key

            if not api_key:
                self._send_json({"error": "Gemini API key is not configured. Please set your key first."}, 400)
                return

            try:
                result = convert_to_catgirl(
                    text=text,
                    api_key=api_key,
                    model=config.get("model", "gemini-2.5-flash"),
                    vibe=vibe,
                    temperature=config.get("temperature", 0.85)
                )
                self._send_json({"result": result})
            except Exception as e:
                self._send_json({"error": str(e)}, 500)

        elif parsed.path == "/api/key":
            new_key = payload.get("key", "").strip()
            if not new_key:
                self._send_json({"error": "Empty key"}, 400)
                return
            config, config_path = load_config()
            config["gemini_api_key"] = new_key
            save_config(config, config_path)
            self._send_json({"success": True})

        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        # Mute normal HTTP access logs for clean console
        return

def run_server():
    server_address = ("127.0.0.1", PORT)
    try:
        httpd = ThreadingHTTPServer(server_address, CatgirlHTTPHandler)
    except OSError:
        # Port busy, find alternate port
        httpd = ThreadingHTTPServer(("127.0.0.1", PORT + 1), CatgirlHTTPHandler)
        server_address = ("127.0.0.1", PORT + 1)

    url = f"http://localhost:{server_address[1]}"
    print(f"\n🐾 NekoText Web GUI started at: {url}")
    print("Press Ctrl+C to stop the server nya~!\n")

    # Open browser
    try:
        webbrowser.open(url)
    except Exception:
        pass

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping web server... Sayonara nya~!")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run_server()
