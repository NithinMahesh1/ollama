import os
import json
import requests
import sqlite3

# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`
model = "llama3"  # TODO: update this for whatever model you wish to use


def chat(messages):
    print(messages)
    r = requests.post(
        "http://0.0.0.0:11434/api/chat",
        json={"model": model, "messages": messages, "stream": True},
        stream=True
    )
    r.raise_for_status()
    output = ""

    with open(os.path.join('','output.txt'),'w') as f:
        for line in r.iter_lines():
            print(line, file=f)
            body = json.loads(line)
            if "error" in body:
                raise Exception(body["error"])
            if body.get("done") is False:
                message = body.get("message", "")
                content = message.get("content", "")
                output += content
                # the response streams one token at a time, print that as we receive it
                print(content, end="", flush=True)

            if body.get("done", False):
                message["content"] = output
                return message


def main():
    # TODO create DB only if a chat.db does not exist in dir
    # createDB()
    messages = []

    # TODO modify this with Sqlite3:
    #   Create two tables one for input and one for output
    #   Table "Output" Columns:
    #       - id: primary key
    #       - model: LLM model being used to add data
    #       - message: message content in the form of VARCHAR (one whole response from model)
    #       - date_created: keep track of times we made these requests so we can build timeline for model
    #       - lineObj: the actual object that is being passed (possibly for training data later)
    #   Table "Input" Columns:
    #       - model: LLM model name that is being sent the user input
    #       - message: user input message content in the form of VARCHAR as well
    #       - date_created: time for user inputs to compare to response from models
    count = 0
    while True:
        with open(os.path.join('','input.txt'),'w') as f:
            user_input = input("Enter a prompt: ")
            if not user_input:
                exit()
            print(user_input,file=f)
            print()
            # Intercept it here
            count += 1
            print("This is the count: " +count)
            messages.append({"role": "user", "content": user_input})
            message = chat(messages)
            messages.append(message)
            print("\n\n")


if __name__ == "__main__":
    main()
