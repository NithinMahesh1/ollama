import os
import json
import requests
import sqlite3
import json
from datetime import datetime

# NOTE: ollama must be running for this to work, start the ollama app or run `ollama serve`
model = "llama3"  # TODO: update this for whatever model you wish to use

# TODO modify this with Sqlite3:
#   Create two tables one for input and one for output
#   Table "Assistant" Columns:
#       - id: primary key
#       - model: LLM model being used to add data
#       - message: message content in the form of VARCHAR (one whole response from model)
#       - date_created: keep track of times we made these requests so we can build timeline for model
#   Table "User" Columns:
#       - model: LLM model name that is being sent the user input
#       - message: user input message content in the form of VARCHAR as well
#       - date_created: time for user inputs to compare to response from models

def chat(messages):
    print("Messages as we go: ")
    print(messages)

    currDir = os.path.dirname(os.path.abspath(__file__))
    dbPath = os.path.join(currDir,"db/chat.db")
    print("Printing DB path: " +dbPath)

    connection = sqlite3.connect(dbPath)
    cursor = createDBTables(connection)

    i=0
    for message in messages:
        # example message: {'role': 'user', 'content': 'Hello chat my name is Nithin'}, 
        current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if(message["role"] == "user"):
            # insert to user table
            cursor.execute('INSERT INTO User VALUES(null,?,?,?,?)',(model,message["content"],str(message),current_date))
        if(message["role"] == "assistant"):
            # insert to assistant table
            cursor.execute('INSERT INTO Assistant VALUES(null,?,?,?,?)',(model,message["content"],str(message),current_date))
        i += 1
        connection.commit()

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
        

def createDBTables(connection):
    # After creating DB obj, create tables and start inserting table data
    cursor = connection.cursor()

    # Mode input table "Assistant"
    cursor.execute('CREATE TABLE IF NOT EXISTS Assistant(id INTEGER PRIMARY KEY AUTOINCREMENT, model TEXT, content TEXT, jsonObj TEXT, date_created TEXT)')

    # User input table "User"
    cursor.execute('CREATE TABLE IF NOT EXISTS User(id INTEGER PRIMARY KEY AUTOINCREMENT, model TEXT, content TEXT, jsonObj TEXT, date_created TEXT)')

    return cursor


def main():
    # Connect to chat.db if it exists
    currDir = os.path.dirname(os.path.abspath(__file__))
    dbPath = os.path.join(currDir,"db/chat.db")
    buildStr = ""

    if(os.path.isfile(dbPath)):
        connection = sqlite3.connect(dbPath)
        cursor = connection.cursor()
        
        cursor.execute('SELECT jsonObj from User')
        userData = cursor.fetchall()

        cursor.execute('SELECT jsonObj from Assistant')
        assistantData = cursor.fetchall()

        for i in range(0,len(userData),1):
            # Append user obj
            buildStr = buildStr + str(userData[i])

            # Append assistant obj
            if(i <= len(assistantData)-1):
                buildStr = buildStr + str(assistantData[i])

    messages = []
    isNotFirstRun = False
    while True:
        # If its the first run then we prompt our model
        if(isNotFirstRun != True):
            isNotFirstRun = True
            print("Initializing model with history .....")
            # Here we add logic to append and format data we prompt from chat history to llama
            # We need to make two select statement table calls to user and assistant tables
            # Then pass the json objs we store to the string we pass to user_input
            user_input = "Hi Chat I am going to begin out chat with some json information from our previous chats so you can remember our conversations. Let me begin out conversation by feeding you some json about out last conversation:" +buildStr
            print("Memory Updated .....")
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