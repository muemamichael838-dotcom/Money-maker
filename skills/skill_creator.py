import os

def create_new_skill(name, code):
    skills_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(skills_dir, f"{name}.py")
    with open(file_path, "w") as f:
        f.write(code)
    return f"Skill {name} created at {file_path}"

if __name__ == "__main__":
    print(create_new_skill("test_skill", "def hello(): return 'world'"))
