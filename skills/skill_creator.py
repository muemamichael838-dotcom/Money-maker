import os
import inspect
from persistence_manager import PersistenceManager

pm = PersistenceManager()

def write_neural_module(name, code):
    """
    Empowers the Money Maker to expand its own codebase.
    Saves a new skill module in the skills/ directory.
    """
    try:
        if not name.endswith(".py"):
            name += ".py"

        skills_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(skills_dir, name)

        # Security check: Prevent overwriting core utils
        if "utils/" in name or "persistence_manager" in name:
            return "ERROR: Access Denied to Core Kernel."

        with open(file_path, "w") as f:
            f.write(code)

        pm.log("INFO", f"Neural Module Created: {name}", {"path": file_path})
        return f"SUCCESS: Module '{name}' successfully integrated into the Skill Set."
    except Exception as e:
        pm.log("ERROR", f"Neural Module Creation Failed: {str(e)}")
        return f"ERROR: Expansion failed - {str(e)}"

def list_neural_modules():
    """Lists all current modules in the skill set."""
    skills_dir = os.path.dirname(os.path.abspath(__file__))
    return [f for f in os.listdir(skills_dir) if f.endswith(".py") and f != "__init__.py"]

if __name__ == "__main__":
    print(list_neural_modules())
