import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from constants import *

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

def print_usage(usage_metadata):
    prompt_tokens = usage_metadata.prompt_token_count
    response_tokens = usage_metadata.candidates_token_count
    print(f"Prompt tokens: {prompt_tokens}\nResponse tokens: {response_tokens}")

def output_conversation(user_prompt,  response):
    if len(sys.argv) > 2:
        if sys.argv[2] == VERBOSE:
            print(f"User prompt: {user_prompt}\n")
            print(f"Gemini response: {response.text}")
            print_usage(response.usage_metadata)
    else:
        print(response.text)

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
        contents=messages
    )

    output_conversation(user_prompt, response)


if __name__ == "__main__":
    main()
