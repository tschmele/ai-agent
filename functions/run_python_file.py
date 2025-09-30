import os
import subprocess
from config import *

def process_output(result: subprocess.CompletedProcess[bytes]) -> str:
    output: str = f"STDOUT: {result.stdout}\nSTDERR: {result.stderr}"
    if result.returncode != 0:
        output += f"\nProcess exited with code {result.returncode}"
    if len(result.stdout) == 0:
        output += "\nNo output produced."
    return output

def run_python_file(working_directory: str, file_path: str, args=[]) -> str:
    try:
        rel_path = os.path.join(working_directory, file_path)
        if not os.path.abspath(rel_path).startswith(os.path.abspath(working_directory)):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.exists(rel_path):
            return f'Error: File "{file_path}" not found.'
        if not file_path.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file.'
        
        command = [
            "uv",
            "run",
            file_path
        ]
        if len(args) > 0:
            command += args

        try:
            result = subprocess.run(args=command, timeout=CODE_TIMEOUT, capture_output=True, cwd=working_directory)
        except Exception as e:
            return f"Error: executing Python file: {e}"

        return process_output(result)
    except Exception as e:
        return f"Error: {e}"