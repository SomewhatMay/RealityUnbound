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
is_loading_chat = False
is_querying = False

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

class ConfirmDeleteDialog(ctk.CTkToplevel):
    def __init__(self, parent, callback):
        super().__init__(parent)
        self.title("Confirm Delete")
        self.transient(parent)

        self.result = None
        self.callback = callback

        message_label = ctk.CTkLabel(self, text="Are you sure you want to delete this save?")
        message_label.pack(padx=20, pady=20)

        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(padx = 10, pady = 10)

        yes_button = ctk.CTkButton(button_frame, text="Yes", command=self.on_yes, fg_color="red", hover_color="darkred")
        yes_button.pack(side="left", padx=10)

        no_button = ctk.CTkButton(button_frame, text="No", command=self.on_no)
        no_button.pack(side="right", padx=10)

    def on_yes(self):
        self.result = True
        self.callback(self.result)
        self.destroy()

    def on_no(self):
        self.result = False
        self.callback(self.result)
        self.destroy()

class Sidebar(ctk.CTkScrollableFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.grid(row = 1, column = 0, columnspan = 3, padx = 10, pady = 10, sticky = "nsew")
        
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
            command = lambda: app.loadChat(chatInfo)
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
            command = lambda: self.removeRequest(chatInfo, chatButton)
        )
        # removeButton.grid(column = 1, row = itemsLen, pady = (0, 10), sticky = "nsew")
        
        removeButton.place(relx = 1, x = -25)
    
    def removeRequest(self, chatInfo, button):
        def delete_callback(result):
            if result:
                self.remove(chatInfo, button)
            else:
                print("User doesn't want to delete window!")

        app.wait_window(ConfirmDeleteDialog(app, delete_callback))
    
    def remove(self, chatInfo, button):
        button.destroy()
        savedChatsDB.pop(chatInfo["name"])
        
        with open("savedChats.json", "w") as savedChatsJson:
                json.dump(savedChatsDB, savedChatsJson, indent=4)
    
    def loadAll(self):
        for chatName in savedChatsDB:
            chatInfo = savedChatsDB[chatName]
            self.add(chatInfo)

class ChatBubble(ctk.CTkFrame):
    def __init__(self, parent, role):
        super().__init__(parent)

        roleName = "Reality Unbound" if role == "assistant" else "user"
        color = "#0c84fe" if role == "system" else "#7bdf3e"

        self.grid_rowconfigure(0, weight = 0, minsize = 20)
        self.grid_rowconfigure(1, weight = 1)

        mainLabel = ctk.CTkLabel(
            self,
            fg_color = color,
            padx = 10,
            pady = 10,
            font = (ctk.CTkFont, 13),
            corner_radius = 8,
            wraplength = 500,  
            justify = "left",  
            anchor = "w",
            text = ""
        )
        mainLabel.grid(column = 0, row = 1, sticky = "nsew")

        userLabel = ctk.CTkLabel(
            self,
            fg_color = "transparent",
            padx = 5,
            pady = 10,
            text = roleName,
            font = (ctk.CTkFont, 14),
            justify = "left",
            anchor = "w"
        )
        userLabel.grid(column = 0, row = 0, sticky = "nsew")

        self.userLabel = userLabel
        self.mainLabel = mainLabel
    
    def setText(self, text):
        self.mainLabel.configure(text = text)
        
    def animateText(self, text, counter=1):
        self.configure(text = text[:counter])
        
        if counter < len(text):
            app.after(150, lambda: self.animateText(self, text, counter + 1))       

class MessagesWindow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.grid(row = 0, column = 0, sticky = "nsew")

        self.canvas = ctk.CTkCanvas(self, bg="#2b2b2b", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self, command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

        self.messages = []

        self.index = 0
    
    def add_message(self, messageInfo):
        # Create a new label for the message
        message_label = ChatBubble(self.scrollable_frame, messageInfo["role"])
        message_label.setText(messageInfo["role"] + " -> " + messageInfo["content"])
        message_label.pack(side="top", fill="both", expand=True, pady = 5, padx = 10)

        # Add the label to the messages list
        self.messages.append(message_label)

        # Automatically scroll to the bottom
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")     

class MainWindow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color = "transparent")
        self.grid(column = 3, row = 1, sticky = "nswe", padx = (0, 10), pady = 10)
        
        # Menu screen
        
        startAdventureButton = ctk.CTkButton(
            self, 
            text = "Start New Adventure"
        )
        # startAdventureButton.grid(column = 1, row = 1)

        self.startAdventureButton = startAdventureButton

        # Chat screen

        topBar = ctk.CTkLabel(
            parent, 
            text = "Reality Unbound", 
            anchor = "w",
            fg_color = "#2b2b2b",
            corner_radius = 8
        )
        
        topBar.grid(column = 3, row = 0, sticky = "nsew", padx = (0, 10), pady = (10, 0))
        self.topBar = topBar
        
        messagesWindow = MessagesWindow(self)
        
        chatBox = ctk.CTkEntry(
            self,
            placeholder_text = "Type here..."
        )
        
        sendChatIcon = ImageTk.PhotoImage(Image.open("assets/SendChat.png").resize((20, 20), Image.Resampling.BILINEAR))
        sendButton = ctk.CTkButton(
            self,
            text = "",
            image = sendChatIcon,
            width = 30,
            #command = self.sendMessage
        )
        
        self.messagesWindow = messagesWindow
        self.chatBox = chatBox
        self.sendButton = sendButton
        
        self.chatScreen()

    def menuScreen(self):
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)
        self.grid_columnconfigure(2, weight = 1)
        
        self.grid_rowconfigure(0, weight = 1)
        self.grid_rowconfigure(1, weight = 1)
        self.grid_rowconfigure(2, weight = 1)
        
        # Load the button
        self.startAdventureButton.grid(row = 1, column = 1)
        
        # the other stuff
        #self.topBar.grid(row = 0, column = 0, columnspan = 3)
        self.messagesWindow.forget()
        self.chatBox.forget()
        self.sendButton.forget()
        
    def chatScreen(self):
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 0, minsize = 30)
        self.grid_columnconfigure(2, weight = 0)
        
        self.grid_rowconfigure(0, weight = 1)
        self.grid_rowconfigure(1, weight = 0, minsize = 30)
        self.grid_rowconfigure(2, weight = 0)
        
        self.startAdventureButton.forget()
        
        #self.topBar.grid(row = 0, column = 0, columnspan = 2)
        self.messagesWindow.grid(row = 0, column = 0, columnspan = 2, sticky = "nsew")
        self.chatBox.grid(row = 1, column = 0, sticky = "nsew", padx = (0, 10), pady = (10, 0))
        self.sendButton.grid(row = 1, column = 1, pady = (10, 0))

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Reality Unbound")
        self.geometry("1000x600")
        
        self.minsize(width = 1000, height = 600)
        
        # Grid configuration
        
        self.grid_columnconfigure(0, weight = 0, minsize = 150)
        self.grid_columnconfigure(1, weight = 0)
        self.grid_columnconfigure(2, weight = 0)
        self.grid_columnconfigure(3, weight = 1)
        
        self.grid_rowconfigure(0, weight = 0, minsize = 30)
        self.grid_rowconfigure(1, weight = 1)
        
        # Inner windows
        
        self.sidebar = Sidebar(self)
        self.mainWindow = MainWindow(self)
        
        sidebarTitleContainer = ctk.CTkFrame(self)
        sidebarTitleContainer.grid(row = 0, column = 0, padx = 10, pady = (10, 0), sticky="nsew")
        
        sidebarTitle = ctk.CTkLabel(sidebarTitleContainer, text = "Chats")
        sidebarTitle.pack()
        
        saveChatIcon = ImageTk.PhotoImage(Image.open("assets/SaveIcon.png").resize((20, 20), Image.Resampling.BILINEAR))
        saveChatButton = ctk.CTkButton(self, image = saveChatIcon, text = "", width = 30, command = self.saveChat)
        saveChatButton.grid(row = 0, column = 2, padx = (0, 10), pady = (10, 0), sticky="nsew")
        
        newChatButton = ctk.CTkButton(self, text = "+", width = 30)
        newChatButton.grid(row = 0, column = 1, padx = (0, 10), pady = (10, 0), sticky="nsew")

    def saveChat(self):
        chatName = ctk.CTkInputDialog(text = "Name your chat", title = "Save Chat").get_input()
        
        if chatName != None:
            chatName = str(chatName)
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
    global app
    app = App()
    app.mainloop()
    
    # newUserAction()