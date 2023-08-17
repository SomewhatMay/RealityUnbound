import openai
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import atexit
import uuid
import json
import random
import time
import tokens

### Variables ###
MODEL = "gpt-3.5-turbo"
openai.api_key = tokens.openAiToken()
sessionId = "session-" + str(uuid.uuid4())

mock_data = True

with open("responses.json", "r") as responseJson:
    responseDB = json.load(responseJson)

with open("mockResponses.json", "r") as mockresponsesJson:
    mockResponsesDB = json.load(mockresponsesJson)

with open("savedChats.json", "r") as savedChatsJson:
    savedChatsDB = json.load(savedChatsJson)

sessionInfo = {
    "tokenUsage" : {
        "outbound" : 0,
        "inbound" : 0
    },
    
    "responses" : []
}

currentChatName = sessionId
messages = [
    {
        "role" : "system",
        "content" : "You simulate what happens in the video game. The messages will contain what the player chooses to do. You are to respond with the consequences/results of the player's action. Whatever you output will be directly sent to the player's screen. Please do not spoil the game, please take it slow; Keep the responses concise as this is a text-based story game and people don't want to read too much. Unless you are explaining something specific, please keep your responses between 1-2 sentences. Give the players at least three choices per message throughout the story and always put a fourth choice saying (Type your own action...). Try to lead the player onto a story that is roughly 10 choices long or 2 minutes long. Ensure the story has a satisfying ending and plot but try to incorporate plot twists. Ensure that sometimes, the player's choice does not turn out to be the way they invisioned and it backfires. Also ensure that the player can actually die and either end the game or restart at checkpoint; make sure death is possible but unlikely and avoidable! Please start off by introducing the game to the player.",
    },
]


def addMessage(role, content, name = None):
    roleString = ""
    
    if role == 0:
        roleString = "system"
    elif role == 1:
        roleString = "assistant"
    elif role == 2:
        roleString = "user"
    
    messages.append({
        "role": roleString,
        "name": name,
        "content": content
    })
    
    print(roleString + ": " + content)

def makeCompletion():
    message = ""
    
    if mock_data:
        response = mockResponsesDB[random.randint(0, len(mockResponsesDB) - 1)]
        
        message = response["choices"][0]["message"]["content"]
    else:
        # response = openai.ChatCompletion.create(
        #     model = MODEL,
        #     messages = messages,
        #     temperature = .7,
        #     max_tokens = 1024,
        #     stop = None,
        #     top_p = .8,
        # )
        
        # print(response)
        # message = response["choices"][0]["message"]["content"]
        # print("Called API!")
        print("API disabled!")
        
    
    addMessage(1, message)
    
    
    
    return message

class Sidebar(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row = 1, column = 0, columnspan = 2, padx = 10, pady = 10, sticky = "nsew")
        
        self.grid_columnconfigure(0, weight = 1)
        self.items = []
        
        self.loadAll()
    
    
    def add(self, chatInfo):
        chatButton = ctk.CTkButton(
            self, 
            text = chatInfo["name"], 
            fg_color = "#242424", 
            hover_color = "#1D1D1D", 
            anchor = "w",
        )
        
        itemsLen = len(self.items)
        chatButton.grid(row = itemsLen, column = 0, padx = 0, pady = (0, 10), sticky = "nwe")
        self.items.append(chatButton)
        
        removeButton = ctk.CTkButton(
            chatButton,
            text = "X",
            fg_color = "#242424",
            hover_color = "#1D1D1D",
            width = 20,
            command = lambda: self.remove(chatInfo, chatButton)
        )
        # removeButton.grid(column = 1, row = itemsLen, pady = (0, 10), sticky = "nsew")
        
        removeButton.place(relx = 1, x = -25)
    
    def remove(self, chatInfo, button):
        button.destroy()
        savedChatsDB.pop(chatInfo["name"])
        
        with open("savedChats.json", "w") as savedChatsJson:
                json.dump(savedChatsDB, savedChatsJson, indent=4)
    
    def loadAll(self):
        for chatName in savedChatsDB:
            chatInfo = savedChatsDB[chatName]
            self.add(chatInfo)

class MainWindow(ctk.CTKFrame):
    def __init__(self, parent):
        super().__init__(parent)
        

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Reality Unbound")
        self.geometry("1000x600")
        
        self.minsize(width = 1000, height = 600)
        
        # Grid configuration
        
        self.grid_columnconfigure(0, weight = 0, minsize = 300)
        self.grid_columnconfigure(1, weight = 0)
        self.grid_columnconfigure(2, weight = 10)
        
        self.grid_rowconfigure(0, weight = 0, minsize = 30)
        self.grid_rowconfigure(1, weight = 1)
        
        # Inner windows
        
        self.sidebar = Sidebar(self)
        
        sidebarTitleContainer = ctk.CTkFrame(self)
        sidebarTitleContainer.grid(row = 0, column = 0, padx = 10, pady = (10, 0), sticky="nsew")
        
        sidebarTitle = ctk.CTkLabel(sidebarTitleContainer, text = "Chats")
        sidebarTitle.pack()
        
        saveChatIcon = ImageTk.PhotoImage(Image.open("assets/SaveIcon.png").resize((20, 20), Image.Resampling.BILINEAR))
        newChatButton = ctk.CTkButton(self, image = saveChatIcon, text = "", width = 30, command = self.saveChat)
        newChatButton.grid(row = 0, column = 1, padx = (0, 10), pady = (10, 0), sticky="nsew")
    
    
    def saveChat(self):
        chatName = str(ctk.CTkInputDialog(text = "Name your chat", title = "Save Chat").get_input())
        
        if chatName != None:
            chatinfo = {
                "name" : chatName,
                "savedTime" : time.time(),
                "messages" : messages
            }
            freshChat = chatName in savedChatsDB
            savedChatsDB[chatName] = chatinfo
            
            with open("savedChats.json", "w") as savedChatsJson:
                json.dump(savedChatsDB, savedChatsJson, indent=4)
            
            if not freshChat:
                self.sidebar.add(chatinfo)
            

def newUserAction(userMessage = None):
    if userMessage == "exit()":
        exit()
    elif userMessage != None:
        addMessage(2, userMessage)

    makeCompletion()
    newUserAction(input())

def atExit():
    if len(sessionInfo["responses"]) > 0:
        responseDB["tokenUsage"]["outbound"] += sessionInfo["tokenUsage"]["outbound"]
        responseDB["tokenUsage"]["inbound"] += sessionInfo["tokenUsage"]["inbound"]
        responseDB["sessions"][sessionId] = sessionInfo
        
        with open("responses.json", "w") as responseJson:
            json.dump(responseDB, responseJson, indent=4)

atexit.register(atExit)
    
if not mock_data:
    print("Mock data is disabled, are you sure you want to proceed? (y/N)")
    
    result = input()
    
    if result.lower() != "y":
        print("Closing program...")
        exit()

if __name__ == "__main__":
    app = App()
    app.mainloop()
    
    # newUserAction()