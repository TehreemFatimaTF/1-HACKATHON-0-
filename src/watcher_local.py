import time
import os
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Project root
INBOX_DIR = os.path.join(BASE_DIR, "Inbox")
NEEDS_ACTION_DIR = os.path.join(BASE_DIR, "Needs_Action")
LOGS_DIR = os.path.join(BASE_DIR, "Logs")

# Ensure directories exist
for directory in [INBOX_DIR, NEEDS_ACTION_DIR, LOGS_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

class LocalFileWatcher:
    """Watches local Inbox folder for new files"""

    def __init__(self):
        self.running = False
        self.log_file = os.path.join(LOGS_DIR, "watcher_local.log")

    def log(self, message, level="INFO"):
        """Log messages to file and console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [LOCAL] [{level}] {message}"
        print(log_entry)

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")

    def start(self):
        """Start watching local Inbox folder"""
        self.running = True
        self.log("=== Local File Watcher Starting ===", "SYSTEM")
        self.log(f"Monitoring: {INBOX_DIR}")
        self.log(f"Output to: {NEEDS_ACTION_DIR}")

        class LocalFileHandler(FileSystemEventHandler):
            def __init__(self, watcher):
                self.watcher = watcher

            def on_created(self, event):
                if not event.is_directory:
                    filename = os.path.basename(event.src_path)

                    # Ignore hidden and temp files
                    if filename.startswith('.') or filename.startswith('~'):
                        return

                    self.watcher.log(f"New file detected: {filename}")
                    self.process_file(event.src_path, filename)

            def process_file(self, src_path, filename):
                try:
                    # Wait for file to be fully written
                    time.sleep(0.5)

                    with open(src_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Move to Needs_Action with metadata
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
                    new_filename = f"task_{timestamp}_{filename}"
                    if not new_filename.endswith('.md'):
                        new_filename += '.md'

                    dest_path = os.path.join(NEEDS_ACTION_DIR, new_filename)

                    # Add metadata
                    metadata = f"---\nSource: Local_File\nDetected_At: {timestamp}\nStatus: Unprocessed\n---\n\n"

                    with open(dest_path, 'w', encoding='utf-8') as f:
                        f.write(metadata + content)

                    # Remove original file
                    os.remove(src_path)
                    self.watcher.log(f"Processed: {new_filename}")

                except Exception as e:
                    self.watcher.log(f"Error processing {filename}: {e}", "ERROR")

        handler = LocalFileHandler(self)
        observer = Observer()
        observer.schedule(handler, INBOX_DIR, recursive=False)
        observer.start()
        self.log("Local file watcher active")

        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
        finally:
            observer.stop()
            observer.join()

    def stop(self):
        """Stop the watcher"""
        self.log("=== Shutting down local file watcher ===", "SYSTEM")
        self.running = False

if __name__ == "__main__":
    watcher = LocalFileWatcher()
    watcher.start()
