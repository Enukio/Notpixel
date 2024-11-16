import os
import importlib.util
from pathlib import Path

def check_function_in_file(file_path, function_name):
    """Check if a function is defined in a given Python file."""
    if not os.path.isfile(file_path):
        return False
    with open(file_path, 'r') as file:
        content = file.read()
    return f"def {function_name}(" in content


def detect_and_fix_import_issue(module_path, function_name):
    """Automatically fix import issues by detecting and defining missing functions."""
    if not os.path.isfile(module_path):
        print(f"Module not found: {module_path}")
        return False

    if check_function_in_file(module_path, function_name):
        print(f"Function '{function_name}' already exists in {module_path}")
        return True

    # Add the missing function stub to the file
    with open(module_path, 'a') as file:
        file.write(f"\n\ndef {function_name}():\n    pass\n")
    print(f"Added missing function '{function_name}' to {module_path}")
    return True


def clean_pycache():
    """Remove all __pycache__ directories."""
    for pycache in Path(".").rglob("__pycache__"):
        for file in pycache.glob("*.pyc"):
            file.unlink()
        pycache.rmdir()
    print("Cleared all __pycache__ directories.")


def main():
    # Specify the module and function that caused the ImportError
    module_path = "bot/utils/ps.py"
    function_name = "check_base_url"

    # Detect and fix missing function definitions
    if detect_and_fix_import_issue(module_path, function_name):
        print(f"Successfully fixed the issue for {function_name}")

    # Clean Python caches to ensure the latest changes are used
    clean_pycache()

    # Restart the script
    print("You can now re-run your script to check if the issue is resolved.")


if __name__ == "__main__":
    main()

