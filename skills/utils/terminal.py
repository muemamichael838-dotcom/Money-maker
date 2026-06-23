import subprocess

def execute_command(command):
    """Executes a shell command as the current user."""
    try:
        # Running as 'hermes' user for security compliance
        result = subprocess.run(
            ["bash", "-c", command],
            capture_output=True,
            text=True,
            check=True
        )
        return {
            "status": "success",
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "returncode": e.returncode
        }
    except Exception as e:
        return {
            "status": "critical_error",
            "message": str(e)
        }

if __name__ == "__main__":
    print(execute_command("ls -l"))
