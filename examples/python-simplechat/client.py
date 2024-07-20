import os
import json
import requests
import sqlite3

# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`
model = "llama3"  # TODO: update this for whatever model you wish to use

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

def chat(messages):
    print("Messages as we go: ")
    print(messages)
    r = requests.post(
        "http://0.0.0.0:11434/api/chat",
        json={"model": model, "messages": messages, "stream": True},
        stream=True
    )
    r.raise_for_status()
    output = ""

    for line in r.iter_lines():
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
    isNotFirstRun = False
    while True:
        # If its the first run then we prompt our model
        if(isNotFirstRun != True):
            isNotFirstRun = True
            print("Initializing model with history .....")
            user_input = "Hi Chat I am going to begin out chat with some json information from our previous chats so you can remember our conversations. Let me begin out conversation by feeding you some json about out last conversation:[{'role': 'user', 'content': 'Hello chat my name is Nithin'}, {'role': 'assistant', 'content': 'Nice to meet you, Nithin! Welcome to the conversation. What brings you here today? Do you have a specific topic in mind or would you like me to suggest some fun conversations we can have?'}, {'role': 'user', 'content': 'I want to teach you a few things about me for your context with our future conversations. Lets begin with some background about me, I am currently a software engineer at NEAG (The New England Appliance Group) and my past company was Aras Corporation. Some more things I am a .net developer and asp.net web developer.'}]"
        else:
            user_input = input("Enter a prompt: ")
            if not user_input:
                exit()
            print()
        
        messages.append({"role": "user", "content": user_input})
        message = chat(messages)
        messages.append(message)
        print("\n\n")


if __name__ == "__main__":
    main()
