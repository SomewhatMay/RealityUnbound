import openai
from pathlib import Path
import threading
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import atexit
import uuid
import json
import random
import copy
import time


### Variables ###
MODEL = "gpt-3.5-turbo"

token_exists = False
if Path("./tokens.py"):
    try:
        import tokens
        token_exists = True
        openai.api_key = tokens.openAIToken()
    except:
        print("No module named tokens!")

sessionId = "session-" + str(uuid.uuid4())

mock_data = False
is_loading_chat = False
is_querying = False
is_type_writing_response = False
add_new_mock_responses= True

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
deafult_messages = [
    {
        "role" : "system",
        "content" : "You simulate what happens in the video game. The messages will contain what the player chooses to do. You are to respond with the consequences/results of the player's action. Whatever you output will be directly sent to the player's screen. Please do not spoil the game, please take it slow; Keep the responses concise as this is a text-based story game and people don't want to read too much. Unless you are explaining something specific, please keep your responses between 1-2 sentences. Give the players at least three choices per message throughout the story and always put a fourth choice saying (Type your own action...). Try to lead the player onto a story that is roughly 10 choices long or 2 minutes long. Ensure the story has a satisfying ending and plot but try to incorporate plot twists. Ensure that sometimes, the player's choice does not turn out to be the way they invisioned and it backfires. Also ensure that the player can actually die and either end the game or restart at checkpoint; make sure death is possible but unlikely and avoidable! You are NOT a chat assistant, you are only the logic behind the game; please treat each and every message from the user as an action",
    },
]

app = None
currentChatName
messages = deafult_messages


def _typewriter_help(textable, value, requiredIndex, counter=1):
    global is_type_writing_response
     
    try: 
        currentIndex = textable._type_writer_index

        if not (currentIndex == requiredIndex):
            return

        textable.configure(text = value[:counter])
        
        try:
            if textable.is_chat_bubble == True:
                app.mainWindow.messagesWindow.move_to_bottom()
                is_type_writing_response = True
        except:
            pass
                
        if counter < len(value):
            app.after(6, lambda: _typewriter_help(textable, value, requiredIndex, counter + 1))
        else:
            try:
                if textable.is_chat_bubble == True:
                    is_type_writing_response = False
            except:
                pass
    except:
        is_type_writing_response = False


def typewriter(textable, value):
    try:
        currentIndex = textable._type_writer_index
    except:
        currentIndex = 0
        textable._type_writer_index = 0

    currentIndex += 1
    textable._type_writer_index = currentIndex

    _typewriter_help(textable, value, currentIndex)


def is_empty_string(string):
    return (string == None) or (string == " ") or (string == "")


class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, titleText, confirmText, callback):
        super().__init__(app)
        self.title(titleText)
        self.transient(app)
        self.grab_set()

        self.result = None
        self.callback = callback

        message_label = ctk.CTkLabel(self, text=confirmText, wraplength=300)
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
        chatButton.grid(row = itemsLen, column = 0, padx = 0, pady = (0, 5), sticky = "nwe")
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

        app.wait_window(ConfirmDialog("Confirm Delete", "Are you sure you want to delete this save?", delete_callback))
    
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
        
        roleName = None
        color = None
        anchor = None
        justify = None
        column = None
        sticky = None

        if role == "assistant":
            roleName = "Reality Unbound"
            color = "#26252a"
            anchor = "w"
            justify = "left"
            sticky = "nsw"
            column = 0
        else:
            roleName = "You"
            color = "#0c84fe"
            anchor = "e"
            justify = "right"
            sticky = "nse"
            column = 1

            # empty_content = ctk.CTkFrame(self)
            # empty_content.grid(column = 0, row = 1, sticky="ew")

        self.grid_rowconfigure(0, weight = 0, minsize = 20)
        self.grid_rowconfigure(1, weight = 1)

        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 1)

        mainLabel = ctk.CTkLabel(
            self,
            fg_color = color,
            padx = 10,
            pady = 10,
            font = (ctk.CTkFont, 13),
            corner_radius = 8,
            wraplength = 1070,  
            justify = justify,  
            anchor = anchor,
            text = "",
        )

        mainLabel.grid(column = column, row = 1, sticky = sticky)
        mainLabel.is_chat_bubble = True

        userLabel = ctk.CTkLabel(
            self,
            fg_color = "transparent",
            padx = 5,
            pady = 10,
            text = roleName,
            font = (ctk.CTkFont, 14),
            justify = justify,
            anchor = anchor
        )
        userLabel.grid(column = column, row = 0, sticky = sticky)

        self.userLabel = userLabel
        self.mainLabel = mainLabel
    
    def setText(self, text):
        self.mainLabel.configure(text = text)
        
    def animateText(self, text):
        typewriter(self.mainLabel, text)


class MessagesWindow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.grid(row = 0, column = 0, sticky = "nsew", pady = (0, 10))

        self.canvas = ctk.CTkCanvas(self, bg="#2b2b2b", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self, command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas, fg_color="transparent")

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        
        # print(parent.winfo_width())
        # empty_content = ctk.CTkFrame(self.scrollable_frame, bg_color="transparent", height = 0, width = parent.winfo_width() - 150)
        # empty_content.pack(side = "top", fill = "both", expand = True)

        self.messages = []
    
    def add_message(self, messageInfo):
        # Create a new label for the message
        message_label = ChatBubble(self.scrollable_frame, messageInfo["role"])
        message_label.pack(side="top", fill="both", expand=True, pady = (5, 0), padx = 10)

        # Add the label to the messages list
        self.messages.append(message_label)

        # self.move_to_bottom()

        return message_label

    def move_to_bottom(self, moveTopFirst=False):
        # Automatically scroll to the bottom
        if moveTopFirst == True:
            self.canvas.yview_moveto(0)
        
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")     
    
    def unload_messages(self):
        for message in self.messages:
            message.destroy()
        
        self.messages = []
    
    def load_messages(self):
        for messageInfo in messages:
            if messageInfo["role"] == "system":
                continue

            new_label = self.add_message(messageInfo)
            new_label.setText(messageInfo["content"]) # instantly set the text instead of animating it
        

        self.move_to_bottom(True)


class MainWindow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color = "transparent")
        self.grid(column = 3, row = 1, sticky = "nswe", padx = (0, 10), pady = 10)
        
        # Menu screen
        
        startAdventureButton = ctk.CTkButton(
            self, 
            text = "Begin New Adventure",
            command = lambda: app.newChat()
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
        chatBox.bind("<Return>", lambda e: self.sendMessage())
        
        sendChatIcon = ImageTk.PhotoImage(Image.open("assets/SendChat.png").resize((20, 20), Image.Resampling.BILINEAR))
        sendButton = ctk.CTkButton(
            self,
            text = "",
            image = sendChatIcon,
            width = 30,
            command = self.sendMessage
        )
        
        self.messagesWindow = messagesWindow
        self.chatBox = chatBox
        self.sendButton = sendButton
        
        self.menuScreen()

    def sendMessage(self):
        global is_loading_chat, is_querying, is_type_writing_response

        if (is_loading_chat == True) or (is_querying == True) or (is_type_writing_response == True):
            return
        
        messageContent = str(self.chatBox.get())
        self.chatBox.select_range(0, len(messageContent) - 1)
        self.chatBox.delete(0, tk.END)
        
        if is_empty_string(messageContent):
            return
        
        messageInfo = {
            "role": "user",
            "content": messageContent,
        }

        userMessage = app.newMessage(messageInfo)
        userMessage.setText(messageContent)
        self.messagesWindow.move_to_bottom()

        app.saveChat(currentChatName)

        app.makeCompletion()

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
        self.messagesWindow.place(relx = 2)
        self.chatBox.forget()
        self.sendButton.forget()
        
    def chatScreen(self):
        self.grid_columnconfigure(0, weight = 1)
        self.grid_columnconfigure(1, weight = 0, minsize = 30)
        self.grid_columnconfigure(2, weight = 0)
        
        self.grid_rowconfigure(0, weight = 1)
        self.grid_rowconfigure(1, weight = 0, minsize = 30)
        self.grid_rowconfigure(2, weight = 0)
        
        self.startAdventureButton.place(relx = 2)
        
        #self.topBar.grid(row = 0, column = 0, columnspan = 2)
        self.messagesWindow.grid(row = 0, column = 0, columnspan = 2, sticky = "nsew")
        self.chatBox.grid(row = 1, column = 0, sticky = "nsew", padx = (0, 10), pady = (10, 0))
        self.sendButton.grid(row = 1, column = 1, pady = (10, 0))

    def setTopBar(self, text):
        typewriter(self.topBar, text)


class NewJourneyWindow(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()

        self.title("New Journey")
        
        # Label for naming the journey
        label_name = ctk.CTkLabel(self, text="Name your new journey (optional, leave blank for random story):")
        label_name.pack(pady=10, padx = "30")

        # Text box for naming the journey
        self.entry_name = ctk.CTkEntry(self)
        self.entry_name.pack(pady=5)
        self.entry_name.focus_force()

        # Label for additional context
        label_context = ctk.CTkLabel(self, text="Additional context (optional, leave blank for random plot):")
        label_context.pack(pady=10)

        # Text box for additional context
        self.entry_context = ctk.CTkEntry(self)
        self.entry_context.configure()
        self.entry_context.pack(pady=5)

        # Frame for buttons
        button_frame = ctk.CTkFrame(self, bg_color = "transparent", fg_color = "transparent")
        button_frame.pack(pady=10)

        # Start Adventure button
        start_button = ctk.CTkButton(button_frame, text="Start Adventure", command=self.start_adventure)
        start_button.pack(side="right", padx=10)

        # Cancel button
        cancel_button = ctk.CTkButton(button_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side="left", padx=10)

    def start_adventure(self):
        newChatName = str(self.entry_name.get())
        newStoryDescription = str(self.entry_context.get())
        newMessages = copy.deepcopy(deafult_messages)
        hasAdditionalContext = False
        additionalContext = " The user has provided additional context on story. If these strings are empty, ignore them."

        if not is_empty_string(newChatName):
            hasAdditionalContext = True
            additionalContext += f" Name of story: \"{newChatName}\"."

        if not is_empty_string(newStoryDescription):
            hasAdditionalContext = True
            additionalContext += f" Plot context: \"{newStoryDescription}\"."

        if hasAdditionalContext == True:
            newMessages[0]["content"] += additionalContext
        
        newMessages[0]["content"] += " Please begin by explaining and introducing the game to the player."

        chatInfo = {
            "name": newChatName,
            "savedTime": time.time(),
            "messages": newMessages
        }
        
        print(chatInfo)

        app.loadChat(chatInfo)
        app.saveChat(chatInfo["name"])
        self.destroy()

        app.makeCompletion()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Reality Unbound")
        self.geometry("1400x900")
        self.resizable(False, True)
        
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
        
        newChatButton = ctk.CTkButton(self, text = "+", width = 30, command = self.newChat)
        newChatButton.grid(row = 0, column = 1, padx = (0, 10), pady = (10, 0), sticky="nsew")

        if not token_exists:
            tokenDialogue = ctk.CTkInputDialog(text = "No OpenAI Token found. Please enter in a token to continue or else mock data will be used! (ONLY FOR TESTING, DATA IS VERY INACCURATE)")
            result = tokenDialogue.get_input()

            global mock_data
            if result != None:
                openai.api_key = tokens.openAIToken(result)
            else:
                mock_data = True

        if not mock_data:
            ConfirmDialog("API usage warning!", "Mock data is disabled, are you sure you want to proceed?", self.mock_data_result)


    def makeCompletion(self):
        global is_loading_chat, is_querying

        if is_loading_chat or is_querying:
            return

        is_querying = True

        def fetch_openai_response():
            global is_querying
            response = None
            
            messageInfo = {
                "role": "assistant",
                "content": "loading..."
            }
            
            responseMessage = self.mainWindow.messagesWindow.add_message(messageInfo)
            app.mainWindow.messagesWindow.move_to_bottom()
            
            def dot(currentText = "."):
                if response != None:
                    return

                responseMessage.setText("Determining your fate" + currentText)
                
                if currentText == ".":
                    currentText = ".."
                elif currentText == "..":
                    currentText = "..."
                elif currentText == "...":
                    currentText = "."
                
                app.after(250, lambda: dot(currentText))

            dot()
            
            if mock_data:
                time.sleep(3)
                response = mockResponsesDB[random.randint(0, len(mockResponsesDB) - 1)]
            else:
                try:
                    response = openai.ChatCompletion.create(
                        model=MODEL,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1024,
                        stop=None,
                        top_p=0.8,
                    )
                except Exception as e:
                    print("There was an error! " + repr(e))
                    ConfirmDialog("Runtime Error", "There was an exception getting a response from OpenAI: " + repr(e), lambda x: True)

                print("APIResponse: \n" + str(response))

                if add_new_mock_responses:
                    mockResponsesDB.append(response)
                    with open("mockResponses.json", "w") as mockresponsesJson:
                        json.dump(mockResponsesDB, mockresponsesJson, indent=4)

            sessionInfo["responses"].append(response)
            sessionInfo["tokenUsage"]["outbound"] += response["usage"]["prompt_tokens"]
            sessionInfo["tokenUsage"]["inbound"] += response["usage"]["completion_tokens"]

            messageInfo["content"] = response["choices"][0]["message"]["content"]
            responseMessage.animateText(messageInfo["content"])
            messages.append(messageInfo)

            is_querying = False
            app.saveChat(currentChatName)

        # Create a separate thread for the API request
        api_thread = threading.Thread(target=fetch_openai_response)
        api_thread.start()


    def newMessage(self, messageInfo):
        print(messages)
        messages.append(messageInfo)
        return self.mainWindow.messagesWindow.add_message(messageInfo)


    def mock_data_result(self, result):
       if result != True:
           self.destroy()


    def newChat(self):
        global is_loading_chat, is_querying

        if (is_loading_chat == True) or (is_querying == True):
            return

        newChatWindow = NewJourneyWindow()
        newChatWindow.grab_set()


    def loadChat(self, chatInfo):
        global is_loading_chat, is_querying

        if (is_loading_chat == True) or (is_querying == True):
            return

        global messages, currentChatName

        is_loading_chat = True

        self.mainWindow.messagesWindow.unload_messages()

        messages = chatInfo["messages"]
        currentChatName = chatInfo["name"]

        self.mainWindow.chatScreen()
        self.mainWindow.setTopBar(currentChatName)
        self.mainWindow.messagesWindow.load_messages()

        is_loading_chat = False


    def saveChat(self, chatName=None):
        global is_loading_chat, is_querying, currentChatName

        if (is_loading_chat == True) or (is_querying == True):
            return

        chatName = chatName if chatName else ctk.CTkInputDialog(text = "Name your chat", title = "Save Chat").get_input()
        
        if not is_empty_string(chatName):
            chatName = str(chatName)
            currentChatName = chatName
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
        

def atExit():
    if len(sessionInfo["responses"]) > 0:
        responseDB["tokenUsage"]["outbound"] += sessionInfo["tokenUsage"]["outbound"]
        responseDB["tokenUsage"]["inbound"] += sessionInfo["tokenUsage"]["inbound"]
        responseDB["sessions"][sessionId] = sessionInfo
        
        with open("responses.json", "w") as responseJson:
            json.dump(responseDB, responseJson, indent=4)

atexit.register(atExit)

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")

    app = App()
    app.mainloop()