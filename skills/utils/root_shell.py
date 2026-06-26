import subprocess
import os

def execute_command(command):
    """Executes a bash command with root-level access in the container."""
    try:
        # We are running as root by default or have passwordless sudo
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "code": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    print(execute_command("id"))
