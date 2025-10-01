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

str_to_function = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file
}

total_tokens: dict[str,int] = {
    "prompt_tokens":0,
    "response_tokens":0
}

def print_usage(usage_metadata: types.GenerateContentResponseUsageMetadata) -> None:
    prompt_tokens = usage_metadata.prompt_token_count
    response_tokens = usage_metadata.candidates_token_count
    print(f"Prompt tokens: {prompt_tokens}\nResponse tokens: {response_tokens}")

def call_function(function_call_part: types.FunctionCall, verbose: bool=False) -> types.Content:
    function_name = function_call_part.name if function_call_part.name is not None else "None"
    args = function_call_part.args if function_call_part.args is not None else {}
    if function_name not in str_to_function:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    
    try:
        function_result = str_to_function[function_name](working_directory=WORKING_DIRECTORY, **args)
    except Exception as e:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Error: {e}"},
                )
            ],
        )
  
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )

def generate_content(messages: list[types.Content], verbose: bool=False) -> None:
    terminate_loop = False
    for i in range(MAX_ITERATIONS):
        try:
            response: types.GenerateContentResponse = client.models.generate_content(
                model=MODEL, 
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], 
                    system_instruction=SYSTEM_PROMPT
                )
            )
        except Exception as e:
            print(f"Error: generate_content failed: {str(e)}")
            exit(1)

        if (response.usage_metadata is not None 
                and response.usage_metadata.prompt_token_count is not None 
                and response.usage_metadata.candidates_token_count is not None):
            total_tokens["prompt_tokens"] += response.usage_metadata.prompt_token_count
            total_tokens["response_tokens"] += response.usage_metadata.candidates_token_count

        if response.candidates is not None:
            messages += [c.content for c in response.candidates if c.content is not None]
        
        if response.function_calls is not None:
            for call in response.function_calls:
                if verbose:
                    print(f"Calling function: {call.name}({call.args})")
                else:
                    print(f" - Calling function: {call.name}")
                
                function_call_result: types.Content = call_function(call, verbose)

                if function_call_result.parts is not None and function_call_result.parts[0].function_response is not None:
                    if not hasattr(function_call_result.parts[0].function_response, "response"):
                        raise Exception("Error: We lost the response somewhere.")
                    if verbose:
                        print(f"-> {function_call_result.parts[0].function_response.response}")
                    messages.append(types.Content(role="user", parts=[function_call_result.parts[0]]))

        elif response.text is not None:
            print(f"Final Response:")
            print(f"{response.text}\n")
            terminate_loop = True
        
        else:
            print(f"Error: Response contains neither function_calls nor text.")

        if verbose and response.usage_metadata is not None:
            print_usage(response.usage_metadata)
        if terminate_loop:
            break


def main():
    if len(sys.argv) <= 1:
        print("No prompt provided")
        exit(1)
    user_prompt = sys.argv[1]
    verbose = True if len(sys.argv) > 2 and VERBOSE in sys.argv[2:]  else False
    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)])
    ]
    if verbose:
        print(f"User prompt: {user_prompt}\n")

    generate_content(messages, verbose)

    print(f"Total tokens used:")
    print(f"Prompt tokens: {total_tokens['prompt_tokens']}")
    print(f"Response tokens: {total_tokens['response_tokens']}")

if __name__ == "__main__":
    main()
