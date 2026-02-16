# Watcher System Architecture

## Overview
The watcher system has been modularized into separate, independent components for better maintainability and scalability.

## File Structure

```
src/
├── watcher.py              # Main orchestrator (runs all watchers)
├── watcher_local.py        # Local file system monitoring
├── watcher_gmail.py        # Gmail inbox monitoring
└── watcher_linkedin.py     # LinkedIn trends monitoring
```

## Architecture

### Main Orchestrator (watcher.py)
- Manages all watcher threads
- Handles graceful startup/shutdown
- Provides unified logging
- Configuration management

### Individual Watchers

Each watcher is a standalone module that can:
- Run independently for testing
- Be enabled/disabled via config
- Log to its own file
- Handle errors gracefully

## Running Watchers

### Run All Watchers (Recommended)
```bash
python src/watcher.py
```

### Run Individual Watchers (For Testing)
```bash
# Test local file watcher only
python src/watcher_local.py

# Test Gmail watcher only
python src/watcher_gmail.py

# Test LinkedIn watcher only
python src/watcher_linkedin.py
```

## Configuration

Edit `SOURCES_CONFIG` in `src/watcher.py`:

```python
SOURCES_CONFIG = {
    "local_files": True,      # Always enabled
    "gmail": False,           # Set to True after Gmail MCP setup
    "linkedin": True          # Simulated for demo
}
```

## Log Files

Each watcher maintains its own log:

```
Logs/
├── watcher_main.log        # Main orchestrator logs
├── watcher_local.log       # Local file watcher logs
├── watcher_gmail.log       # Gmail watcher logs
└── watcher_linkedin.log    # LinkedIn watcher logs
```

## How It Works

### 1. Local File Watcher (watcher_local.py)
- Monitors: `Inbox/` folder
- Triggers: When new file is created
- Action: Moves file to `Needs_Action/` with metadata
- Technology: Python watchdog library

### 2. Gmail Watcher (watcher_gmail.py)
- Monitors: Gmail inbox (via MCP)
- Triggers: Every 60 seconds
- Action: Creates markdown file in `Inbox/` for each new email
- Technology: Gmail MCP (when configured)

### 3. LinkedIn Watcher (watcher_linkedin.py)
- Monitors: LinkedIn trends (simulated)
- Triggers: Every 120 seconds
- Action: Creates markdown file in `Inbox/` for each trend
- Technology: LinkedIn API (simulated for demo)

## Threading Model

```
Main Thread (watcher.py)
├── Thread 1: LocalFileWatcher
├── Thread 2: GmailWatcher (if enabled)
└── Thread 3: LinkedInWatcher (if enabled)
```

All threads run as daemons and stop gracefully on Ctrl+C.

## Adding New Watchers

To add a new watcher (e.g., Slack, WhatsApp):

1. Create `src/watcher_[name].py`
2. Implement class with `start()` and `stop()` methods
3. Add to `SOURCES_CONFIG` in `watcher.py`
4. Import and register in `watcher.py`

Example:

```python
# src/watcher_slack.py
class SlackWatcher:
    def __init__(self):
        self.running = False

    def start(self):
        self.running = True
        # Your monitoring logic

    def stop(self):
        self.running = False
```

Then in `watcher.py`:

```python
from watcher_slack import SlackWatcher

SOURCES_CONFIG = {
    # ... existing config
    "slack": True
}

# In start() method:
if SOURCES_CONFIG["slack"]:
    self.start_watcher("Slack", SlackWatcher)
```

## Error Handling

Each watcher handles its own errors:
- Logs errors to its own log file
- Continues running despite errors
- Main orchestrator monitors thread health

## Testing

Test individual watchers:

```bash
# Test local watcher
cd src
python watcher_local.py
# Drop a file in Inbox/ and verify it moves to Needs_Action/

# Test LinkedIn watcher
python watcher_linkedin.py
# Wait 2 minutes and check Inbox/ for LinkedIn trend file

# Test Gmail watcher
python watcher_gmail.py
# Verify it logs "MCP not configured yet"
```

## Performance

- Local watcher: Real-time (uses OS file system events)
- Gmail watcher: 60-second polling interval
- LinkedIn watcher: 120-second polling interval
- Memory: ~50MB per watcher
- CPU: <1% when idle

## Benefits of Modular Design

1. **Testability**: Each watcher can be tested independently
2. **Maintainability**: Changes to one watcher don't affect others
3. **Scalability**: Easy to add new sources
4. **Debugging**: Separate logs for each component
5. **Flexibility**: Enable/disable sources via config
6. **Reusability**: Watchers can be used in other projects

## Troubleshooting

**Import errors:**
```bash
# Make sure you're in the project root
cd C:\Users\HP 15\OneDrive\Documents\HACKATHON-0-PERSONAL-AI-EMPLOYEE\SILVER-TIER\Ai_Employee_vault

# Run from root, not from src/
python src/watcher.py
```

**Watcher not starting:**
- Check log files in `Logs/` directory
- Verify dependencies: `pip install watchdog requests python-dotenv`
- Ensure directories exist: `Inbox/`, `Needs_Action/`, `Logs/`

**No files being created:**
- Check watcher logs for errors
- Verify source is enabled in `SOURCES_CONFIG`
- For local watcher: Drop a test file in `Inbox/`
- For LinkedIn: Wait 2 minutes for first trend

## Future Enhancements

- [ ] Add Slack watcher
- [ ] Add WhatsApp watcher
- [ ] Add Twitter/X watcher
- [ ] Add RSS feed watcher
- [ ] Add webhook receiver
- [ ] Add health check endpoint
- [ ] Add metrics dashboard
- [ ] Add rate limiting
- [ ] Add retry logic
- [ ] Add circuit breaker pattern
