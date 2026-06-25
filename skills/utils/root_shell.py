import subprocess
import os

def execute_as_root(command):
    """
    Executes a command with root privileges if the agent has sudo access.
    The agent is configured in Dockerfile with NOPASSWD for hermes user.
    """
    try:
        # Check if we are already root
        if os.geteuid() == 0:
            full_cmd = command
        else:
            full_cmd = f"sudo {command}"

        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

def install_system_dependency(package_name):
    """Allows the agent to install system-level tools dynamically."""
    return execute_as_root(f"apt-get update && apt-get install -y {package_name}")
