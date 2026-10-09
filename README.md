# 🐾 NekoText: Anime Catgirl Mode Converter

Turn any text into kawaii anime catgirl speech using Google's Gemini API!

---

## ⚡ Quick Start

### 1. Set your Gemini API Key
Open [config.json](file:///home/gabriel/catgirl-converter/config.json) and replace `"YOUR_GEMINI_API_KEY_HERE"` with your Gemini API key:
```json
{
  "gemini_api_key": "YOUR_ACTUAL_GEMINI_API_KEY",
  "model": "gemini-3.5-flash-lite",
  "temperature": 0.85,
  "default_vibe": "kawaii",
  "auto_copy_clipboard": false
}
```
*(You can get a free API key at [Google AI Studio](https://aistudio.google.com/app/apikey)).*

> Alternatively, you can run `catgirl` directly and it will prompt you to paste your key on the first run, saving it automatically! Or set `export GEMINI_API_KEY="your_key"`.

---

## 🚀 How to Run

Because `catgirl` is linked to `~/.local/bin`, you can run it from anywhere in your terminal:

### Option A: Interactive Mode (REPL)
```bash
catgirl
```
Type any sentence, press <kbd>Enter</kbd>, and watch it convert!
- Change vibe on the fly: `:vibe tsundere`, `:vibe hyper`, `:vibe sleepy`, `:vibe villain`
- Copy last output to clipboard: `:copy`
- Open Web GUI: `:web`
- Change key: `:key`
- Exit: `exit` or `quit`

### Option B: Direct Command Line
```bash
catgirl "I need to deploy this bugfix to production immediately."
```
```bash
catgirl -v tsundere "Hey, are you free to grab coffee this afternoon?"
```
```bash
catgirl -v hyper "Look at this new game update!"
```

### Option C: Pipe / Stdin
```bash
echo "Server restart completed successfully." | catgirl
```

### Option D: Copy Output to Clipboard Automatically
```bash
catgirl -c "Meeting moved to 3 PM."
```

### Option E: Visual Web App
```bash
catgirl-web
# or
catgirl --web
```
Opens a cute pastel browser interface on `http://localhost:7860` with preset buttons and 1-click clipboard copy!

---

## 🎭 Catgirl Vibes
| Vibe | Style |
| :--- | :--- |
| **kawaii** *(default)* | Classic sweet, cheerful, nekomimi with cute puns and kaomojis |
| **tsundere** | "B-Baka!", pouting, reluctant translation with hidden sweetness |
| **hyper** | 1000% zoomies energy, chaotic caps, running across the ceiling |
| **sleepy** | Cozy, slow, purring kotatsu catgirl taking a nap |
| **villain** | "Ohohoho~!", dramatic anime catgirl aristocrat |

---

## 📁 Files
- [catgirl.py](file:///home/gabriel/catgirl-converter/catgirl.py) - Main CLI and REPL tool
- [config.json](file:///home/gabriel/catgirl-converter/config.json) - Your API key and preferences
- [web_app.py](file:///home/gabriel/catgirl-converter/web_app.py) - Standalone local web server GUI
