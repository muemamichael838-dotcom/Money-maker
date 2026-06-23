import os

def create_new_skill(name, code):
    """Creates a new skill file."""
    skills_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(skills_dir, f"{name}.py")
    with open(file_path, "w") as f:
        f.write(code)
    return f"Skill {name} created at {file_path}"

def delete_skill(name, confirmed=False):
    """Deletes a skill file. Requires explicit user confirmation."""
    if not confirmed:
        return "ERROR: Deletion requires human-in-the-loop confirmation. Please set 'confirmed=True'."

    skills_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(skills_dir, f"{name}.py")

    if os.path.exists(file_path):
        os.remove(file_path)
        return f"SUCCESS: Skill {name} has been deleted."
    else:
        return f"ERROR: Skill {name} not found."

if __name__ == "__main__":
    print(delete_skill("test_skill", confirmed=False))
