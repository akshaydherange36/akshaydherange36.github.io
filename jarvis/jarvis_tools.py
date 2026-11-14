"""Tools JARVIS can use on your machine.

Each function decorated with @beta_tool becomes a tool Claude can call.
The docstring (including Args) is what Claude reads to decide when and
how to use the tool — keep them accurate.
"""

import datetime
import platform
import shlex
import subprocess
import threading
import webbrowser

import psutil
from anthropic import beta_tool

OS = platform.system()  # "Darwin", "Windows", "Linux"


@beta_tool
def get_current_time() -> str:
    """Get the current local date and time."""
    return datetime.datetime.now().strftime("%A, %B %d %Y, %I:%M %p")


@beta_tool
def open_application(app_name: str) -> str:
    """Open a desktop application on the user's computer.

    Args:
        app_name: The application's name, e.g. "Spotify", "Google Chrome",
            "notepad", "firefox". Use the name as it appears on this OS.
    """
    try:
        if OS == "Darwin":
            subprocess.run(["open", "-a", app_name], check=True, timeout=15)
        elif OS == "Windows":
            subprocess.run(f'start "" "{app_name}"', shell=True, check=True, timeout=15)
        else:  # Linux
            subprocess.Popen([app_name.lower().replace(" ", "-")],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Opened {app_name}."
    except Exception as exc:  # noqa: BLE001 — report any failure back to the model
        return f"Could not open {app_name}: {exc}"


@beta_tool
def open_website(url: str) -> str:
    """Open a URL in the user's default web browser.

    Args:
        url: Full URL including scheme, e.g. "https://github.com".
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opened {url} in the browser."


@beta_tool
def get_system_status() -> str:
    """Report CPU, memory, disk usage and battery level of this computer."""
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    lines = [
        f"CPU: {cpu:.0f}%",
        f"Memory: {mem.percent:.0f}% used ({mem.used / 1e9:.1f} of {mem.total / 1e9:.1f} GB)",
        f"Disk: {disk.percent:.0f}% used ({disk.free / 1e9:.1f} GB free)",
    ]
    battery = psutil.sensors_battery() if hasattr(psutil, "sensors_battery") else None
    if battery is not None:
        state = "charging" if battery.power_plugged else "on battery"
        lines.append(f"Battery: {battery.percent:.0f}% ({state})")
    return "\n".join(lines)


@beta_tool
def search_web(query: str) -> str:
    """Search the web and return the top results with titles, URLs and snippets.

    Args:
        query: The search query.
    """
    try:
        from ddgs import DDGS
        results = list(DDGS().text(query, max_results=5))
        if not results:
            return "No results found."
        return "\n\n".join(
            f"{r.get('title', '')}\n{r.get('href', '')}\n{r.get('body', '')}"
            for r in results
        )
    except Exception as exc:  # noqa: BLE001
        return f"Search failed: {exc}"


@beta_tool
def set_timer(minutes: float, label: str = "Timer") -> str:
    """Set a timer. When it goes off, JARVIS announces it out loud.

    Args:
        minutes: Duration in minutes (can be fractional, e.g. 0.5 for 30 seconds).
        label: What the timer is for, announced when it fires.
    """
    def fire() -> None:
        message = f"Sir, your timer is up: {label}."
        print(f"\n⏰ {message}")
        try:
            from jarvis_voice import speak
            speak(message)
        except Exception:  # noqa: BLE001 — voice is optional; the print above suffices
            pass

    threading.Timer(minutes * 60, fire).start()
    return f"Timer set for {minutes:g} minute(s): {label}."


@beta_tool
def run_shell_command(command: str, reason: str) -> str:
    """Run a shell command on the user's computer. The user is asked to
    approve the exact command first — use this only when no other tool fits.

    Args:
        command: The exact shell command to run.
        reason: One sentence on why this command is needed (shown to the user).
    """
    print(f"\n🛡️  JARVIS wants to run: {command}\n    Reason: {reason}")
    answer = input("    Allow? [y/N] ").strip().lower()
    if answer not in ("y", "yes"):
        return "The user declined to run this command."
    try:
        result = subprocess.run(
            command if OS == "Windows" else shlex.split(command),
            shell=(OS == "Windows"),
            capture_output=True, text=True, timeout=60,
        )
        output = (result.stdout + result.stderr).strip()
        return output[:4000] if output else f"Command finished with exit code {result.returncode}."
    except Exception as exc:  # noqa: BLE001
        return f"Command failed: {exc}"


ALL_TOOLS = [
    get_current_time,
    open_application,
    open_website,
    get_system_status,
    search_web,
    set_timer,
    run_shell_command,
]
