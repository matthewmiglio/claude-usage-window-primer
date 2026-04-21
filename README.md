# claude-usage-window-primer

Sends a trivial message to Claude Code at ~6:00 AM EST daily so the 5-hour usage window resets by 11:00 AM when you actually need it.

## Stack

- **Python 3.11** — daemon loop with sleep-until-target scheduling
- **Claude Code CLI** — `claude -p` for non-interactive messages
- **Docker** — containerized with `restart: always`

```
┌─────────────────────────────────┐
│         LXC Host Machine        │
│                                 │
│  ~/.claude/ ──────────┐         │
│                       │ mount   │
│  ┌────────────────────▼──────┐  │
│  │     Docker Container      │  │
│  │                           │  │
│  │  Python daemon (main.py)  │  │
│  │    │                      │  │
│  │    ├─ sleep until ~6 AM   │  │
│  │    ├─ claude -p "hey"     │  │
│  │    └─ repeat              │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
```

## Setup

```bash
# Install Node.js + Claude Code on the host
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
sudo apt-get install -y nodejs
npm install -g @anthropic-ai/claude-code

# Login interactively (one-time)
claude

# Verify headless mode works
claude -p "hi"

# Clone and start
git clone https://github.com/matthewmiglio/claude-usage-window-primer.git
cd claude-usage-window-primer
docker-compose up -d
```

## Usage

```bash
docker-compose logs -f hi-claude   # watch logs
docker-compose restart hi-claude   # restart
docker-compose down                # stop
```

The daemon picks a random greeting and adds 0–3 minutes of jitter to avoid exact-same-time requests each day.
