import os
import shutil
from huggingface_hub import HfApi
from persistence_manager import PersistenceManager

def backup_to_hf():
    pm = PersistenceManager()
    token = os.environ.get("HF_TOKEN")
    repo_id = os.environ.get("HF_BACKUP_DATASET") # User should create a dataset for this

    if not token or not repo_id:
        pm.log("WARNING", "HF_TOKEN or HF_BACKUP_DATASET missing. Backup skipped.")
        return

    pm.log("INFO", f"Starting backup to HF Dataset: {repo_id}")
    db_path = os.path.join(os.environ.get("HERMES_HOME", "/opt/data"), "memory.db")

    if not os.path.exists(db_path):
        pm.log("ERROR", "Memory DB not found for backup.")
        return

    try:
        api = HfApi(token=token)
        api.upload_file(
            path_or_fileobj=db_path,
            path_in_repo="memory.db",
            repo_id=repo_id,
            repo_type="dataset"
        )
        pm.log("INFO", "Backup successful.")
    except Exception as e:
        pm.log("ERROR", f"HF Backup failed: {e}")

if __name__ == "__main__":
    backup_to_hf()
