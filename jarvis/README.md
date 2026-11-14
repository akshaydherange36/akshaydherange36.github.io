# JARVIS — Personal AI Assistant

A lightweight, Iron-Man-style voice assistant for your own machine, powered by
the Claude API. Talk to it ("Jarvis, open Spotify") or type to it, and it can:

- **Open apps and websites** on your computer
- **Check system status** — CPU, memory, disk, battery
- **Search the web** and answer from the results
- **Set timers** and announce them out loud
- **Run shell commands** — each one shown to you for approval first
- **Chat** — with JARVIS's dry British personality

It works on macOS, Windows, and Linux. Text mode needs nothing but Python and
an API key; voice mode adds a microphone and two extra packages.

## Setup

1. **Python 3.10+** installed.

2. **Install core dependencies:**

   ```bash
   cd jarvis
   pip install -r requirements.txt
   ```

3. **Get a Claude API key** at <https://platform.claude.com/> and set it:

   ```bash
   # macOS / Linux (add to ~/.zshrc or ~/.bashrc to persist)
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

   ```powershell
   # Windows (persists automatically)
   setx ANTHROPIC_API_KEY "sk-ant-..."
   ```

4. **Run it:**

   ```bash
   python main.py --text
   ```

## Enabling voice

```bash
# macOS first:   brew install portaudio
# Linux first:   sudo apt install portaudio19-dev espeak
pip install -r requirements-voice.txt
python main.py
```

Say **"Jarvis"** followed by your request: *"Jarvis, what's my CPU usage?"*,
*"Jarvis, open YouTube"*, *"Jarvis, set a timer for 10 minutes for the oven"*.
Say *"Jarvis, go to sleep"* to exit. Use `--no-wake` to skip the wake word, or
`--text` to type instead of talk.

- Speech-to-text uses the free Google Web Speech endpoint via the
  `SpeechRecognition` package (needs internet; fine for personal use).
- Text-to-speech uses your OS's built-in voices via `pyttsx3` (offline). It
  picks a British voice if one is installed — on macOS, add "Daniel" under
  System Settings → Accessibility → Spoken Content → System Voice.

## How it works

```
main.py             entry point: wake-word voice loop or text REPL
jarvis_assistant.py Claude agentic loop (tool runner) + JARVIS personality
jarvis_tools.py     the tools Claude can call on your machine
jarvis_voice.py     microphone input + text-to-speech output
```

Each request goes to Claude (model `claude-opus-5-5`) with the tool list; the
SDK's tool runner executes whatever tools Claude calls and loops until it has
an answer. Safety notes:

- `run_shell_command` always prints the exact command and waits for your
  `y/N` approval before running anything.
- A server-side refusal fallback is enabled (`fallbacks="default"`), so if a
  safety classifier declines a request, the API retries it on a fallback model
  automatically.

## Extending it

Add a function to `jarvis_tools.py` with the `@beta_tool` decorator and a good
docstring, append it to `ALL_TOOLS`, and JARVIS can use it. Ideas: control
Spotify via its API, read your calendar, control smart lights, send messages.

## The heavyweight alternative: OpenJarvis

If you outgrow this, [OpenJarvis](https://github.com/open-jarvis/OpenJarvis)
(Stanford, 15k+ stars) is a full local-first agent framework: local models via
Ollama, Whisper speech recognition, neural TTS, scheduled agents, Telegram and
Discord channels, and thousands of importable skills. One-line install:

```bash
curl -fsSL https://open-jarvis.github.io/OpenJarvis/install.sh | bash
```

Then run `jarvis`. It's a much bigger system — this folder is the
understand-every-line version; OpenJarvis is the batteries-included one.
