import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import *
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file
from functions.run_python_file import schema_run_python_file, run_python_file

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file
    ]
)

translate_function = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file
}

def print_usage(usage_metadata: types.GenerateContentResponseUsageMetadata) -> None:
    prompt_tokens = usage_metadata.prompt_token_count
    response_tokens = usage_metadata.candidates_token_count
    print(f"Prompt tokens: {prompt_tokens}\nResponse tokens: {response_tokens}")

def print_function_calls(function_calls: list[types.FunctionCall]) -> None:
    for call in function_calls:
        print(f"Calling function: {call.name}({call.args})")

def call_function(function_call_part: types.FunctionCall, verbose: bool=False) -> types.Content:
    function_name = function_call_part.name if function_call_part.name is not None else "None"
    args = function_call_part.args if function_call_part.args is not None else {}

    if verbose:
        print(f"Calling function: {function_name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_name}")

    if function_name not in translate_function:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    
    function_result = translate_function[function_name](working_directory="./calculator", **args)

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )

def output_conversation(user_prompt,  response: types.GenerateContentResponse) -> None:
    if len(sys.argv) > 2 and sys.argv[2] == VERBOSE:
        print(f"User prompt: {user_prompt}\n")
    print(f"Gemini response: {response.text}")
    if response.function_calls is not None:
        if len(sys.argv) > 2 and sys.argv[2] == VERBOSE:
            for call in response.function_calls:
                function_call_result = call_function(call, verbose=True)
        else:
            for call in response.function_calls:
                function_call_result = call_function(call)
        
        if function_call_result.parts is not None and function_call_result.parts[0].function_response is not None and hasattr(function_call_result.parts[0].function_response, "response"):
            if len(sys.argv) > 2 and sys.argv[2] == VERBOSE:
                print(f"-> {function_call_result.parts[0].function_response.response}")
        else:
            raise Exception("Error: no response?? what happened?")

    if len(sys.argv) > 2 and sys.argv[2] == VERBOSE and response.usage_metadata is not None:
        print_usage(response.usage_metadata)


def main():
    if len(sys.argv) <= 1:
        print("No prompt provided")
        exit(1)
    user_prompt = sys.argv[1]
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)])
    ]
    
    response = client.models.generate_content(
        model=MODEL, 
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], 
            system_instruction=SYSTEM_PROMPT
        )
    )

    output_conversation(user_prompt, response)


if __name__ == "__main__":
    main()
