
import time

from openai_python_cache import create_chat_completion

def main():
    print("Creating chat completion with caching...")
    start_time = time.time()
    response = create_chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! Can you tell me a joke?"}
        ],
        model="gpt-3.5-turbo",
    )
    end_time = time.time()
    print("Response:", response)
    print(f"Time taken: {end_time - start_time} seconds")

if __name__ == "__main__":
    main()
