import subprocess

def execute_as_root(command):
    """Executes a system command with root privileges."""
    try:
        # Since we are already root or have NOPASSWD sudo, this will be seamless
        result = subprocess.run(
            ["sudo", "bash", "-c", command],
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
    print(execute_as_root("whoami"))
