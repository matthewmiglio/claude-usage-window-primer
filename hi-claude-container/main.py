import random
import subprocess
import time
import traceback
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/New_York")
RUN_HOUR = 6
RUN_MINUTE = 0
JITTER_MAX_SECONDS = 180
TIMEOUT_SECONDS = 120

GREETINGS = [
    "hi",
    "hey",
    "yo",
    "wake up!",
    "good morning",
    "morning!",
    "hello there",
    "howdy",
    "rise and shine",
    "top of the morning",
    "sup",
    "hey claude",
    "hi there",
    "greetings",
    "what's up",
    "hola",
    "bonjour",
    "aloha",
    "g'day",
    "heyo",
    "hey hey",
    "waddup",
    "hiya",
    "salutations",
    "yo yo yo",
]


def next_target_time(now: datetime) -> datetime:
    target = now.replace(hour=RUN_HOUR, minute=RUN_MINUTE, second=0, microsecond=0)
    if now >= target:
        target += timedelta(days=1)
    jitter = random.randint(0, JITTER_MAX_SECONDS)
    return target + timedelta(seconds=jitter)


def send_greeting() -> tuple[str, str]:
    greeting = random.choice(GREETINGS)
    result = subprocess.run(
        ["claude", "-p", greeting],
        capture_output=True,
        text=True,
        timeout=TIMEOUT_SECONDS,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude exited {result.returncode}: {result.stderr.strip()}")
    return greeting, result.stdout.strip()


def main() -> None:
    print(f"hi-claude daemon starting. Target: ~{RUN_HOUR:02d}:{RUN_MINUTE:02d} America/New_York (±{JITTER_MAX_SECONDS}s jitter)")

    while True:
        now = datetime.now(TZ)
        target = next_target_time(now)
        sleep_secs = (target - now).total_seconds()
        print(f"Sleeping {sleep_secs:.0f}s until {target.isoformat()}")
        time.sleep(sleep_secs)

        timestamp = datetime.now(TZ).isoformat()
        try:
            greeting, response = send_greeting()
            print(f"[{timestamp}] OK ({greeting!r}): {response[:200]}")
        except Exception:
            print(f"[{timestamp}] FAILED:")
            print(traceback.format_exc())

        time.sleep(60)


if __name__ == "__main__":
    main()
