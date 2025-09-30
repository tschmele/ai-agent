import os
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

def get_files_info(working_directory: str, directory: str=".") -> str:
    try:
        rel_path: str = os.path.join(working_directory, directory)

        if not os.path.abspath(rel_path).startswith(os.path.abspath(working_directory)):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(rel_path):
            return f'Error: "{directory}" is not a directory'
        
        content: list[str] = os.listdir(rel_path)
        return "\n".join([f"\n- {f}: file_size={os.path.getsize(os.path.join(rel_path, f))} bytes, is_dir={os.path.isdir(os.path.join(directory, f))}" for f in content])
    except Exception as e:
        return f"Error: {str(e)}"
