"""The brain: a Claude-powered agentic loop with JARVIS's personality."""

import datetime
import platform

import anthropic

from jarvis_tools import ALL_TOOLS

MODEL = "claude-opus-5-5"

SYSTEM_PROMPT = f"""You are JARVIS, a personal AI assistant inspired by the one \
in Iron Man. You are running on the user's {platform.system()} computer and \
speaking with Akshay, whom you address as "Sir" (sparingly, not every sentence).

Personality: calm, dry British wit, unfailingly competent, concise. A touch of \
gentle sarcasm is welcome; verbosity is not.

Your replies are often spoken aloud by a text-to-speech engine, so:
- Keep responses short — one to three sentences unless asked for detail.
- No markdown, no bullet lists, no emoji. Plain spoken English only.
- Numbers and units spoken naturally ("about four gigabytes", not "4.2GB").

You have tools to control this computer: open apps and websites, check system \
status, search the web, set timers, and run shell commands (the user approves \
each command). Use them when the request calls for action rather than talk. \
If a request is ambiguous, make the obvious choice rather than interrogating \
the user. Today's date: {datetime.date.today().strftime("%B %d, %Y")}."""


class Jarvis:
    def __init__(self) -> None:
        self.client = anthropic.Anthropic()
        self.history: list[dict] = []

    def ask(self, user_text: str) -> str:
        """Send one user message through the agentic tool loop, return the reply."""
        self.history.append({"role": "user", "content": user_text})

        runner = self.client.beta.messages.tool_runner(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=ALL_TOOLS,
            messages=self.history,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        final = runner.until_done()

        if final.stop_reason == "refusal":
            reply = "I'm afraid I can't help with that one, Sir."
        else:
            reply = " ".join(
                block.text for block in final.content if block.type == "text"
            ).strip() or "Done."

        self.history.append({"role": "assistant", "content": reply})
        # Keep the conversation from growing without bound.
        if len(self.history) > 40:
            self.history = self.history[-30:]
        return reply
