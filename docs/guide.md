# Hi Claude: Implementation Guide

Automatically send a trivial message to Claude Code every day at 6:00 AM EST to start the usage window early, so the window resets by 11:00 AM when it's most needed during the workday.

---

## 1) How Claude Code Usage Windows Work

Claude Code usage operates on a **rolling 5-hour window**. The window starts when you send your first message. After 5 hours of usage, the rate limit resets. By sending a throwaway message at 6:00 AM EST, the window opens at 6:00 AM and resets at ~11:00 AM — right when real work begins.

### Key Assumptions

- The usage window is **per-account**, tied to your Anthropic/Claude login
- The window starts on **first interaction**, not on app launch
- A single trivial message (e.g., `"hi"`) is enough to start the window
- Claude Code CLI supports non-interactive mode via `claude -p "message"`

---

## 2) Architecture Overview

```
Docker Container (restart: always)
  └── Python daemon (main.py)
        ├── Sleeps until 6:00 AM EST
        ├── Runs: claude -p "hi"
        └── Repeats daily
```

Three components:

| Component | Purpose |
|---|---|
| **main.py** | Python daemon that sleeps until 6:00 AM EST, invokes `claude -p "hi"`, and repeats daily |
| **Dockerfile** | `python:3.11-slim` container that runs the daemon |
| **docker-compose.yml** | Orchestrates the container with `restart: always` |

---

## 3) Implementation: Python Daemon

### `hi-claude-container/main.py`

The daemon follows the same pattern as the bonsai reminder container:

1. Compute seconds until 6:00 AM EST
2. Sleep until then
3. Run `claude -p "hi"` via `subprocess`
4. Print result to stdout (Docker captures this as container logs)
5. Safety pause (60s) to move past the target minute
6. Repeat forever

### Key Details

- **`claude -p`** runs Claude Code in non-interactive "print" mode — sends the message, prints the response, and exits.
- **Timezone**: Uses `America/New_York` via `zoneinfo` to handle EST/EDT automatically.
- **Subprocess timeout**: 120 seconds — if Claude Code doesn't respond, the attempt is logged as failed and the daemon continues.
- **No log files**: All output goes to stdout; view via `docker-compose logs -f hi-claude`.

---

## 4) Container Setup

### Dockerfile

- Base: `python:3.11-slim`
- Installs Claude Code CLI (npm)
- Copies `main.py`
- Entrypoint: `python -u main.py` (unbuffered for real-time Docker logs)

### docker-compose.yml

- Single service `hi-claude`
- Builds from `./hi-claude-container`
- `restart: always` — auto-restarts on failure or host reboot
- Mounts Claude Code auth from host (so the container can authenticate)

---

## 5) File Structure

```
hi-claude/
├── goal.md                          # What we're trying to accomplish
├── guide.md                         # This document
├── docker-compose.yml               # Container orchestration
├── .dockerignore                    # Build context exclusions
├── hi-claude-container/
│   ├── Dockerfile                   # Container image definition
│   └── main.py                      # Python daemon
└── tests/
    ├── hi-claude.py                 # Test: runs claude -p "hi" and checks for a response
    └── get-time.py                  # Test: prints current time in EST
```

---

## 6) Verification & Troubleshooting

### Verify It's Working

| Check | How |
|---|---|
| **Daemon runs locally** | `python hi-claude-container/main.py` — watch it sleep until 6 AM or test with modified time |
| **Container is running** | `docker-compose ps` |
| **Container logs** | `docker-compose logs -f hi-claude` |
| **Usage window started** | Open Claude Code around 11 AM; if you have fresh capacity, it worked |

### Common Failure Modes

| Symptom | Cause | Fix |
|---|---|---|
| Container exits immediately | `claude` not installed in container | Check Dockerfile installs Node.js + Claude Code CLI |
| `claude -p` returns auth error | Auth credentials not mounted into container | Ensure docker-compose mounts the host's Claude config directory |
| `claude -p` hangs past timeout | Network issue or Claude Code waiting for input | The 120s subprocess timeout handles this; check logs |
| Container restarts in a loop | Unhandled exception in main.py | Check `docker-compose logs` for the traceback |
| Window doesn't reset at 11 AM | Usage window model different than expected | The 5-hour window is an approximation; timing may vary by plan |

---

## 7) Edge Cases

- **EST vs EDT**: Using `America/New_York` handles daylight saving automatically. The message always fires at 6:00 AM local Eastern time.
- **Host reboot**: `restart: always` in docker-compose ensures the container comes back up automatically.
- **Network outage at 6 AM**: The subprocess times out after 120s, the error is logged, and the daemon continues to the next day. No crash.
- **Multiple runs**: The daemon is idempotent. Running the message twice in a day is harmless.
- **Plan/tier changes**: If Anthropic changes usage window mechanics, adjust the target time in `main.py`.
