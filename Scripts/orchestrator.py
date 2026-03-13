import os
import shutil
import time
import logging

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Folders definition
BASE_PATH = "."  # Aapka project root
FOLDERS = {
    "NEEDS_ACTION": os.path.join(BASE_PATH, "Needs_Action"),
    "IN_PROGRESS": os.path.join(BASE_PATH, "In_Progress"),
    "PENDING_APPROVAL": os.path.join(BASE_PATH, "Pending_Approval"),
    "APPROVED": os.path.join(BASE_PATH, "Approved"),
    "DONE": os.path.join(BASE_PATH, "Done")
}

def move_file(filename, source_key, dest_key):
    source = os.path.join(FOLDERS[source_key], filename)
    dest = os.path.join(FOLDERS[dest_key], filename)
    shutil.move(source, dest)
    logger.info(f"Moved {filename} from {source_key} to {dest_key}")

def run_orchestrator():
    logger.info("Orchestrator started watching folders...")
    
    while True:
        # 1. Needs_Action -> In_Progress (Agar koi naya task aaye)
        for filename in os.listdir(FOLDERS["NEEDS_ACTION"]):
            if filename.endswith(".md"): # Sirf task files
                move_file(filename, "NEEDS_ACTION", "IN_PROGRESS")

        # 2. In_Progress -> Pending_Approval (Agar AI apna kaam khatam kar le)
        # Yahan aap logic dal sakte hain ke file ke andar "status: ready" check ho
        for filename in os.listdir(FOLDERS["IN_PROGRESS"]):
            # Yahan simulation: 5 second bad approval ke liye move
            move_file(filename, "IN_PROGRESS", "PENDING_APPROVAL")

        # 3. Pending_Approval -> Approved (Manual check ke baad ya simulation)
        # Aap manual move karke test kar sakte hain
        
        # 4. Approved -> Done (Execution ke baad)
        for filename in os.listdir(FOLDERS["APPROVED"]):
            move_file(filename, "APPROVED", "DONE")
            
        time.sleep(5) # 5 second ka pause taake CPU par load na pare

if __name__ == "__main__":
    run_orchestrator()