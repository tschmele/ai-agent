import os

def generate_response(directory: str, content: list[str]) -> str:
    try:
        return "\n".join(
                [f"\n- {f}: file_size={os.path.getsize(os.path.join(directory, f))} bytes, is_dir={os.path.isdir(os.path.join(directory, f))}" for f in content]
            )
    except Exception as e:
        return f"Error: {str(e)}"

def get_files_info(working_directory: str, directory: str=".") -> str:
    try:
        rel_path: str = os.path.join(working_directory, directory)

        if not os.path.abspath(rel_path).startswith(os.path.abspath(working_directory)):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        if not os.path.isdir(rel_path):
            return f'Error: "{directory}" is not a directory'
        
        content: list[str] = os.listdir(rel_path)
        return generate_response(rel_path, content)
    except Exception as e:
        return f"Error: {str(e)}"
    