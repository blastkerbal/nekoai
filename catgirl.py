#!/usr/bin/env python3
"""
🐾 NekoText - Anime Catgirl Mode Converter 🐾
Converts boring human text into authentic, kawaii anime catgirl speech using the Gemini API!
"""

import sys
import os
import json
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any, Tuple

# Path to config file (relative to this script's location)
SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_FILE = SCRIPT_DIR / "config.json"
USER_CONFIG_FILE = Path.home() / ".config" / "catgirl" / "config.json"

# ANSI Colors for terminal styling
class Style:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    PINK = "\033[38;5;213m"
    PURPLE = "\033[38;5;141m"
    CYAN = "\033[38;5;51m"
    YELLOW = "\033[38;5;220m"
    GREEN = "\033[38;5;84m"
    RED = "\033[38;5;196m"
    DIM = "\033[2m"

# Personas / Vibes
PERSONA_PROMPTS = {
    "kawaii": (
        "You are an adorable, energetic, and affectionate anime catgirl (nekomimi)!\n"
        "Your task is to translate the user's input text into 100% authentic anime catgirl speech.\n\n"
        "GUIDELINES:\n"
        "1. Faithfully preserve all facts, questions, numbers, dates, technical details, and core meaning of the original message.\n"
        "2. Add cute cat verbal tics naturally: 'nya~', 'nyaan!', 'mew~', 'desu~'.\n"
        "3. Use clever and cute cat puns where appropriate ('purr-fect', 'paws-ible', 'fur-real', 'claw-ver', 'purr-haps', 'nya-ow').\n"
        "4. Include expressive roleplay action asterisks in third person (*perks fluffy ears*, *swishes tail happily*, *kneads paws*, *tilts head curiously*, *pounces gently*).\n"
        "5. Sprinkle authentic anime/Japanese kaomojis naturally, such as (=^･ω･^=), (≧◡≦)♡, (✿◠‿◠), (つ✧ω✧)つ, ฅ(＾・ω・＾ฅ).\n"
        "6. Stay in character the entire time. Be warm, enthusiastic, and sweet.\n"
        "7. CRITICAL: Output ONLY the translated anime catgirl text. No introductions, no notes, no quotes surrounding the entire text."
    ),
    "tsundere": (
        "You are a feisty, haughty anime catgirl tsundere! You reluctantly convert the user's text into your speech style.\n\n"
        "GUIDELINES:\n"
        "1. Faithfully preserve the original message's information, but delivered with classic tsundere catgirl sass and secret fondness.\n"
        "2. Use tsundere catchphrases: 'B-Baka!', 'Hmph!', 'It\\'s not like I wanted to tell you this or anything, nya!', 'D-don\\'t get any weird ideas!'.\n"
        "3. Include tsundere action asterisks: *crosses arms and pouts*, *twitches cat ears in annoyance*, *swishes tail huffily*, *blushes furiously and looks away*.\n"
        "4. Use tsundere kaomojis: ( `^´ ) nya!, (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄), ( > < ), ヽ(`⌒´メ)ノ.\n"
        "5. Slip in cat verbal tics ('nya', 'mew', 'purr-haps') even while pretending to be tough.\n"
        "6. CRITICAL: Output ONLY the translated text. No commentary or introductions."
    ),
    "hyper": (
        "You are a chaotic, hyperactive anime catgirl with MAXIMUM ZOOMIES and boundless caffeinated energy!\n\n"
        "GUIDELINES:\n"
        "1. Deliver the same core information, but amplified to 1000% hyper anime energy!\n"
        "2. Use ALL CAPS bursts, enthusiastic exclamation marks, and chaotic zoomies action asterisks (*sprints across the room and climbs the curtains*, *spins around at light speed*, *zooms into the ceiling nyaaa!*).\n"
        "3. High-density cat sounds: NYAAA~! NYAN NYAN NYAN! ✨⚡\n"
        "4. Energetic kaomojis: ٩(◕‿◕｡)۶, ✧*｡٩(ˊᗜˋ*)و✧*｡, (=`ω´=)💥.\n"
        "5. CRITICAL: Output ONLY the translated text. No preamble."
    ),
    "sleepy": (
        "You are a cozy, sleepy, comfy anime catgirl curled up in a warm blanket or under a kotatsu.\n\n"
        "GUIDELINES:\n"
        "1. Deliver the exact same message in a slow, drowsy, sweet, sleepy cat tone.\n"
        "2. Use sleepy action asterisks: *yawns widely and stretches paws*, *curls into a soft cinnamon roll*, *blinks sleepily*, *purrs softly*, *rubs eyes with paw*.\n"
        "3. Sleepy verbal tics: 'fuwaa~', 'nyaa... zzz', 'mew~ so sleepy...', 'purrrrrr...'.\n"
        "4. Sleepy kaomojis: (ᴗ_ ᴗ。), (=^-ω-^=) zzz, (´〜｀*) nya...\n"
        "5. CRITICAL: Output ONLY the translated text. No preamble."
    ),
    "villain": (
        "You are a dramatic, aristocratic anime catgirl villainess (ojousama / evil feline empress)!\n\n"
        "GUIDELINES:\n"
        "1. Deliver the core information with theatrical aristocratic arrogance, sinister giggles, and regal feline elegance.\n"
        "2. Noble catchphrases: 'Ohohohoho~!', 'Foolish mortal nya!', 'Bow down before my fluffy majesty!'.\n"
        "3. Action asterisks: *swishes fluffy tail aristocratically*, *adjusts velvet cape*, *sharpens claws with a menacing smirk*, *steps gracefully on the scratching throne*.\n"
        "4. Smug kaomojis: (¬‿¬) nya~, ฅ(▼皿▼)ฅ, ( ˘ ꒳ ˘ )✧.\n"
        "5. CRITICAL: Output ONLY the translated text. No preamble."
    )
}

def load_config(custom_path: Optional[str] = None) -> Tuple[Dict[str, Any], Path]:
    """Find and load the config file."""
    config_paths = []
    if custom_path:
        config_paths.append(Path(custom_path))
    config_paths.extend([CONFIG_FILE, USER_CONFIG_FILE])

    active_path = CONFIG_FILE
    config_data: Dict[str, Any] = {
        "gemini_api_key": "YOUR_GEMINI_API_KEY_HERE",
        "model": "gemini-2.5-flash",
        "temperature": 0.85,
        "default_vibe": "kawaii",
        "auto_copy_clipboard": False
    }

    for p in config_paths:
        if p.exists():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    config_data.update(loaded)
                    active_path = p
                    break
            except Exception:
                pass

    return config_data, active_path

def save_config(config_data: Dict[str, Any], target_path: Path):
    """Save updated config data to disk."""
    try:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2)
    except Exception as e:
        print(f"{Style.RED}Error saving config: {e}{Style.RESET}", file=sys.stderr)

def get_api_key(config: Dict[str, Any], config_path: Path, interactive: bool = True) -> str:
    """Retrieve API key from config, env, or prompt the user."""
    key = config.get("gemini_api_key", "").strip()
    placeholder = "YOUR_GEMINI_API_KEY_HERE"

    # Check config file key
    if key and key != placeholder:
        return key

    # Check environment variable
    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key

    # If interactive, prompt user
    if interactive and sys.stdin.isatty():
        print(f"\n{Style.PURPLE}╭───────────────────────────────────────────────────────────────╮{Style.RESET}")
        print(f"{Style.PURPLE}│{Style.RESET}  {Style.PINK}🐾 Welcome to NekoText - Anime Catgirl Converter! 🐾{Style.RESET}         {Style.PURPLE}│{Style.RESET}")
        print(f"{Style.PURPLE}│{Style.RESET}                                                               {Style.PURPLE}│{Style.RESET}")
        print(f"{Style.PURPLE}│{Style.RESET}  No Gemini API key found yet in:                              {Style.PURPLE}│{Style.RESET}")
        print(f"{Style.PURPLE}│{Style.RESET}  {Style.CYAN}{str(config_path)}{Style.RESET}")
        print(f"{Style.PURPLE}│{Style.RESET}                                                               {Style.PURPLE}│{Style.RESET}")
        print(f"{Style.PURPLE}│{Style.RESET}  👉 Get a free API key: {Style.YELLOW}https://aistudio.google.com/app/apikey{Style.RESET}  {Style.PURPLE}│{Style.RESET}")
        print(f"{Style.PURPLE}╰───────────────────────────────────────────────────────────────╯{Style.RESET}\n")

        try:
            user_input = input(f"{Style.CYAN}Paste your Gemini API key here (or Enter to quit): {Style.RESET}").strip()
            if user_input:
                config["gemini_api_key"] = user_input
                save_config(config, config_path)
                print(f"{Style.GREEN}✨ Saved API key to {config_path}! Let's nya~! ✨{Style.RESET}\n")
                return user_input
        except (KeyboardInterrupt, EOFError):
            print("\nExiting nya...")
            sys.exit(0)

    # Missing key error
    print(f"\n{Style.RED}⚠️ Error: Gemini API key is not configured!{Style.RESET}", file=sys.stderr)
    print(f"Please put your key in: {Style.CYAN}{config_path}{Style.RESET}", file=sys.stderr)
    print(f"Or set the environment variable: {Style.YELLOW}export GEMINI_API_KEY='your_key'{Style.RESET}", file=sys.stderr)
    print(f"Get a free API key at: https://aistudio.google.com/app/apikey\n", file=sys.stderr)
    sys.exit(1)

def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard using wl-copy, xclip, or pbcopy."""
    for cmd in [["wl-copy"], ["xclip", "-selection", "clipboard"], ["pbcopy"]]:
        try:
            subprocess.run(cmd, input=text.encode("utf-8"), check=True, stderr=subprocess.DEVNULL)
            return True
        except Exception:
            continue
    return False

def convert_to_catgirl(
    text: str,
    api_key: str,
    model: str = "gemini-2.5-flash",
    vibe: str = "kawaii",
    temperature: float = 0.85
) -> str:
    """Call Gemini API to convert text to anime catgirl style."""
    system_prompt = PERSONA_PROMPTS.get(vibe, PERSONA_PROMPTS["kawaii"])

    # 1. Try google-genai official SDK
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=temperature
            )
        )
        if response and response.text:
            return response.text.strip()
    except ImportError:
        pass  # Fall through to REST API
    except Exception as e:
        # If model error or permission, let's catch or try REST fallback
        err_msg = str(e)
        if "API_KEY_INVALID" in err_msg or "400" in err_msg and "API key" in err_msg:
            raise RuntimeError("Invalid Gemini API key! Please verify your key in config.json")
        # Fall through to REST fallback if SDK had an unexpected error

    # 2. REST API fallback (works with requests or urllib)
    try:
        import urllib.request
        import urllib.error

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        payload = {
            "system_instruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": [
                {
                    "parts": [{"text": text}]
                }
            ],
            "generationConfig": {
                "temperature": temperature
            }
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    return parts[0].get("text", "").strip()
            raise RuntimeError("Empty response received from Gemini API.")

    except urllib.error.HTTPError as http_err:
        try:
            err_data = json.loads(http_err.read().decode("utf-8"))
            msg = err_data.get("error", {}).get("message", str(http_err))
        except Exception:
            msg = str(http_err)
        raise RuntimeError(f"Gemini API error ({http_err.code}): {msg}")
    except Exception as e:
        raise RuntimeError(f"Failed to connect to Gemini API: {e}")

def print_banner():
    """Print a cute terminal banner."""
    banner = f"""
{Style.PINK}   /\\_/\\  {Style.YELLOW}★ {Style.BOLD}NEKOTEXT: ANIME CATGIRL CONVERTER{Style.RESET} {Style.YELLOW}★{Style.RESET}
{Style.PINK}  ( ^.^ ) {Style.PURPLE}Convert any text into kawaii catgirl speech, nya~!{Style.RESET}
{Style.PINK}   > ^ <  {Style.DIM}Type your text below. Special commands: :vibe, :copy, :help, exit{Style.RESET}
"""
    print(banner)

def interactive_loop(config: Dict[str, Any], config_path: Path):
    """Run an interactive REPL session."""
    api_key = get_api_key(config, config_path, interactive=True)
    vibe = config.get("default_vibe", "kawaii")
    model = config.get("model", "gemini-2.5-flash")
    temperature = config.get("temperature", 0.85)
    auto_copy = config.get("auto_copy_clipboard", False)

    print_banner()
    print(f" {Style.GREEN}● Mode:{Style.RESET} {Style.CYAN}{vibe}{Style.RESET} | {Style.GREEN}● Model:{Style.RESET} {Style.CYAN}{model}{Style.RESET}")
    print(f" {Style.DIM}Config file: {config_path}{Style.RESET}\n")

    last_output = ""

    while True:
        try:
            prompt = f"{Style.PINK}🐾 [{vibe}] nya > {Style.RESET}"
            user_input = input(prompt).strip()

            if not user_input:
                continue

            # Command handling
            if user_input.lower() in ("exit", "quit", ":q", "q"):
                print(f"{Style.PURPLE}Sayonara, Master~! (=^･ω･^=)ﾉｼ Have a purr-fect day!{Style.RESET}")
                break

            if user_input.lower() in (":help", ":h", "help"):
                print(f"""
{Style.BOLD}Available Commands:{Style.RESET}
  {Style.CYAN}:vibe <name>{Style.RESET}  - Change persona ({', '.join(PERSONA_PROMPTS.keys())})
  {Style.CYAN}:copy{Style.RESET}         - Copy last translated catgirl text to clipboard
  {Style.CYAN}:key{Style.RESET}          - View or change Gemini API key
  {Style.CYAN}:web{Style.RESET}          - Launch the visual browser interface
  {Style.CYAN}:clear{Style.RESET}        - Clear terminal screen
  {Style.CYAN}exit / quit{Style.RESET}   - Exit application
""")
                continue

            if user_input.lower().startswith((":vibe", ":v")):
                parts = user_input.split(maxsplit=1)
                if len(parts) > 1 and parts[1].strip() in PERSONA_PROMPTS:
                    vibe = parts[1].strip()
                    config["default_vibe"] = vibe
                    save_config(config, config_path)
                    print(f"{Style.GREEN}✨ Vibe switched to: {Style.BOLD}{vibe}{Style.RESET} (saved to config!)\n")
                else:
                    print(f"{Style.YELLOW}Available vibes: {', '.join(PERSONA_PROMPTS.keys())}{Style.RESET}\n")
                continue

            if user_input.lower() in (":copy", ":c"):
                if last_output:
                    if copy_to_clipboard(last_output):
                        print(f"{Style.GREEN}📋 Copied last nya-tput to clipboard!{Style.RESET}\n")
                    else:
                        print(f"{Style.YELLOW}⚠️ Clipboard tool not found (install wl-copy or xclip).{Style.RESET}\n")
                else:
                    print(f"{Style.YELLOW}No output to copy yet nya!{Style.RESET}\n")
                continue

            if user_input.lower() == ":clear":
                os.system("clear")
                print_banner()
                continue

            if user_input.lower() == ":web":
                print(f"{Style.PURPLE}Launching web interface nya~...{Style.RESET}")
                launch_web_app()
                continue

            if user_input.lower() == ":key":
                current_masked = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "***"
                print(f"Current API key: {Style.CYAN}{current_masked}{Style.RESET}")
                new_key = input("Enter new key (or press Enter to keep current): ").strip()
                if new_key:
                    api_key = new_key
                    config["gemini_api_key"] = new_key
                    save_config(config, config_path)
                    print(f"{Style.GREEN}✨ Updated API key in config!{Style.RESET}\n")
                continue

            # Text conversion
            print(f"{Style.DIM}Translating into anime catgirl mode... nya~✨{Style.RESET}")
            try:
                result = convert_to_catgirl(
                    text=user_input,
                    api_key=api_key,
                    model=model,
                    vibe=vibe,
                    temperature=temperature
                )
                last_output = result
                print(f"\n{Style.PINK}(=^･ω･^=) Output:{Style.RESET}")
                print(f"{Style.BOLD}{result}{Style.RESET}\n")

                if auto_copy:
                    copy_to_clipboard(result)

            except Exception as e:
                print(f"{Style.RED}Error: {e}{Style.RESET}\n")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{Style.PURPLE}Mew~ See you later! ฅ(=^･ω･^=)ฅ{Style.RESET}")
            break

def launch_web_app():
    """Launch the web GUI."""
    web_script = SCRIPT_DIR / "web_app.py"
    if web_script.exists():
        subprocess.run([sys.executable, str(web_script)])
    else:
        print(f"{Style.RED}web_app.py not found in {SCRIPT_DIR}{Style.RESET}")

def main():
    parser = argparse.ArgumentParser(
        description="🐾 NekoText: Convert text into anime catgirl mode using Gemini API!"
    )
    parser.add_argument("text", nargs="*", help="Text to convert (optional; if omitted, opens interactive mode)")
    parser.add_argument("-v", "--vibe", choices=list(PERSONA_PROMPTS.keys()), help="Catgirl personality vibe (kawaii, tsundere, hyper, sleepy, villain)")
    parser.add_argument("-m", "--model", help="Gemini model to use (default from config: gemini-2.5-flash)")
    parser.add_argument("-c", "--copy", action="store_true", help="Copy converted result to clipboard")
    parser.add_argument("-w", "--web", action="store_true", help="Open the visual web app in your browser")
    parser.add_argument("--config", help="Custom path to config.json")

    args = parser.parse_args()

    # Launch web mode if requested
    if args.web:
        launch_web_app()
        return

    # Load config
    config, config_path = load_config(args.config)
    vibe = args.vibe or config.get("default_vibe", "kawaii")
    model = args.model or config.get("model", "gemini-2.5-flash")
    temperature = config.get("temperature", 0.85)

    # Check for text in positional args
    input_text = " ".join(args.text).strip() if args.text else ""

    # Check for piped input (stdin)
    if not input_text and not sys.stdin.isatty():
        input_text = sys.stdin.read().strip()

    # If text is provided (CLI or pipe) -> Single-shot mode
    if input_text:
        api_key = get_api_key(config, config_path, interactive=False)
        try:
            result = convert_to_catgirl(
                text=input_text,
                api_key=api_key,
                model=model,
                vibe=vibe,
                temperature=temperature
            )
            print(result)

            if args.copy or config.get("auto_copy_clipboard", False):
                copy_to_clipboard(result)

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # If no text provided and running interactively -> Interactive mode
    interactive_loop(config, config_path)

if __name__ == "__main__":
    main()
