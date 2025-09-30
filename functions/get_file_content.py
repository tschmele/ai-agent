import os
from config import *

def get_file_content(working_directory: str, file_path: str) -> str:
    try:
        rel_path = os.path.join(working_directory, file_path)
        if not os.path.abspath(rel_path).startswith(os.path.abspath(working_directory)):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(rel_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(rel_path, "r") as f:
            file_content: str = f.read(MAX_FILE_LENGTH)
            if len(file_content) == MAX_FILE_LENGTH:
                file_content += f'[...File "{rel_path}" truncated at {MAX_FILE_LENGTH} characters]'
            return file_content

    except Exception as e:
        return f"Error: {str(e)}"