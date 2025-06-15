import os

def print_tree(start_path, ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = {"__pycache__", ".git", ".venv", "venv"}

    for root, dirs, files in os.walk(start_path):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        level = root.replace(start_path, '').count(os.sep)
        indent = '│   ' * level + '├── '
        print(f'{indent}{os.path.basename(root)}/')
        subindent = '│   ' * (level + 1)
        for f in files:
            if f.endswith(".pyc") or f == ".DS_Store":
                continue
            print(f'{subindent}{f}')

# Run it
print_tree(".")
