import subprocess
import time

def sync_vault():
    subprocess.run(["git", "pull"])
    # Your changes here
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "Auto sync"])
    subprocess.run(["git", "push"])

while True:
    sync_vault()
    time.sleep(300)  # Har 5 min mein sync