import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CHANGES HERE ---
# OS.GETCWD() use karne se Python khud dhoond lega ke folder kahan hai
BASE_DIR = os.getcwd() 
WATCH_DIRECTORY = os.path.join(BASE_DIR, "Inbox")
DESTINATION_DIRECTORY = os.path.join(BASE_DIR, "Needs_Action")

# Folder check karne ke liye (Safety check)
if not os.path.exists(WATCH_DIRECTORY):
    os.makedirs(WATCH_DIRECTORY)
if not os.path.exists(DESTINATION_DIRECTORY):
    os.makedirs(DESTINATION_DIRECTORY)

class MultiSourceHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            # Temporary files ya hidden files ko ignore karein
            if filename.startswith('.') or filename.startswith('~'):
                return
            print(f"✨ Nayi file detect hui: {filename}")
            self.process_file(event.src_path, filename)

    def process_file(self, src_path, filename):
        timestamp = time.strftime("%Y-%m-%d %H%M%S") # Windows safe timestamp
        new_content = f"---\nSource: Local_File\nDetected_At: {timestamp}\nStatus: Unprocessed\n---\n\n"
        
        try:
            # File ke release hone ka thoda intezar karein (Windows locking issue)
            time.sleep(0.5) 
            
            with open(src_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            new_filename = f"task_{timestamp}_{filename}.md" # Extension .md zaroori hai
            dest_path = os.path.join(DESTINATION_DIRECTORY, new_filename)
            
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(new_content + original_content)
            
            os.remove(src_path)
            print(f"✅ Processed aur move kar di gayi: {new_filename}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    event_handler = MultiSourceHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIRECTORY, recursive=False)
    observer.start()
    print(f"👀 AI Watcher shuru ho gaya...")
    print(f"📂 Monitoring: {WATCH_DIRECTORY}")
    print(f"📤 Moving to: {DESTINATION_DIRECTORY}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()