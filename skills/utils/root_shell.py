import subprocess
import os

def run_system_command(command, use_sudo=True):
    """
    Executes a shell command with root access inside the Docker space.
    """
    try:
        # Docker spaces usually run as root or allow sudo NOPASSWD
        prefix = "sudo " if use_sudo and os.getuid() != 0 else ""
        full_cmd = f"{prefix}{command}"

        result = subprocess.run(
            full_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import sys
    cmd = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "id"
    print(run_system_command(cmd))
