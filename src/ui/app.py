import threading
import random
import time
import copy
import uuid
import customtkinter as ctk
from PIL import Image, ImageTk

import config
import storage
import api
from prompts import deafult_messages
from utils import is_empty_string
from ui.sidebar import Sidebar
from ui.main_window import MainWindow
from ui.dialogs import ConfirmDialog, NewJourneyWindow


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Shared state (formerly module-level globals)
        self.sessionId = "session-" + str(uuid.uuid4())

        self.is_loading_chat = False
        self.is_querying = False
        self.is_type_writing_response = False
        self.add_new_mock_responses = False
        self.mock_data = config.mock_data

        self.responseDB = storage.load_responses()
        self.mockResponsesDB = storage.load_mock_responses()
        self.savedChatsDB = storage.load_saved_chats()

        self.sessionInfo = {
            "tokenUsage": {
                "outbound": 0,
                "inbound": 0
            },

            "responses": []
        }

        self.currentChatName = self.sessionId
        self.messages = copy.deepcopy(deafult_messages)

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

        self.sidebar = Sidebar(self, self)
        self.mainWindow = MainWindow(self, self)

        sidebarTitleContainer = ctk.CTkFrame(self)
        sidebarTitleContainer.grid(row = 0, column = 0, padx = 10, pady = (10, 0), sticky="nsew")

        sidebarTitle = ctk.CTkLabel(sidebarTitleContainer, text = "Chats")
        sidebarTitle.pack()

        saveChatIcon = ImageTk.PhotoImage(Image.open("assets/SaveIcon.png").resize((20, 20), Image.Resampling.BILINEAR))
        saveChatButton = ctk.CTkButton(self, image = saveChatIcon, text = "", width = 30, command = self.makeNewSave)
        saveChatButton.grid(row = 0, column = 2, padx = (0, 10), pady = (10, 0), sticky="nsew")

        newChatButton = ctk.CTkButton(self, text = "+", width = 30, command = self.newChat)
        newChatButton.grid(row = 0, column = 1, padx = (0, 10), pady = (10, 0), sticky="nsew")

        if not api.token_exists:
            tokenDialogue = ctk.CTkInputDialog(text = "No OpenAI Token found. Please enter in a token to continue or else mock data will be used! (ONLY FOR TESTING, DATA IS VERY INACCURATE)")
            result = tokenDialogue.get_input()

            if result != None:
                api.set_api_key(result)
            else:
                self.mock_data = True

        if not self.mock_data:
            ConfirmDialog(self, "API usage warning!", "Mock data is disabled, are you sure you want to proceed?", self.mock_data_result)


    def makeCompletion(self):
        if self.is_loading_chat or self.is_querying:
            return

        self.is_querying = True

        def fetch_openai_response():
            response = None

            messageInfo = {
                "role": "assistant",
                "content": "loading..."
            }

            responseMessage = self.mainWindow.messagesWindow.add_message(messageInfo)
            self.mainWindow.messagesWindow.move_to_bottom()

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

                self.after(250, lambda: dot(currentText))

            dot()

            if self.mock_data:
                time.sleep(3)
                response = self.mockResponsesDB[random.randint(0, len(self.mockResponsesDB) - 1)]
                print(response)
            else:
                try:
                    response = api.fetch_completion(self.messages)
                except Exception as e:
                    print("There was an error! " + repr(e))
                    ConfirmDialog(self, "Runtime Error", "There was an exception getting a response from OpenAI: " + repr(e), lambda x: True)

                print("APIResponse: \n" + str(response))

                if self.add_new_mock_responses:
                    self.mockResponsesDB.append(response)
                    storage.save_mock_responses(self.mockResponsesDB)

            self.sessionInfo["responses"].append(response)
            self.sessionInfo["tokenUsage"]["outbound"] += response["usage"]["prompt_tokens"]
            self.sessionInfo["tokenUsage"]["inbound"] += response["usage"]["completion_tokens"]

            messageInfo["content"] = response["choices"][0]["message"]["content"]
            responseMessage.animateText(messageInfo["content"])
            self.messages.append(messageInfo)

            self.is_querying = False
            self.saveChat(self.currentChatName)

        # Create a separate thread for the API request
        api_thread = threading.Thread(target=fetch_openai_response)
        api_thread.start()


    def newMessage(self, messageInfo):
        self.messages.append(messageInfo)
        return self.mainWindow.messagesWindow.add_message(messageInfo)


    def makeNewSave(self):
        if self.mainWindow.in_menu_screen == True:
            return

        new_chat_name = self.saveChat()
        if not is_empty_string(new_chat_name):
            self.savedChatsDB = storage.load_saved_chats()
            self.loadChat(self.savedChatsDB[new_chat_name])


    def loadByName(self, chatName):
        self.savedChatsDB = storage.load_saved_chats()
        self.loadChat(self.savedChatsDB[chatName])


    def mock_data_result(self, result):
       if result != True:
           self.destroy()


    def newChat(self):
        if (self.is_loading_chat == True) or (self.is_querying == True):
            return

        newChatWindow = NewJourneyWindow(self)
        newChatWindow.grab_set()


    def loadChat(self, chatInfo):
        if (self.is_loading_chat == True) or (self.is_querying == True):
            return

        self.is_loading_chat = True

        self.mainWindow.messagesWindow.unload_messages()

        self.messages = chatInfo["messages"]
        self.currentChatName = chatInfo["name"]

        self.mainWindow.chatScreen()
        self.mainWindow.setTopBar(self.currentChatName)
        self.mainWindow.messagesWindow.load_messages()

        self.is_loading_chat = False


    def saveChat(self, chatName=None):
        if (self.is_loading_chat == True) or (self.is_querying == True):
            return

        chatName = chatName if (not is_empty_string(chatName)) else ctk.CTkInputDialog(text = "Name your chat", title = "Save Chat").get_input()

        if not is_empty_string(chatName):
            self.savedChatsDB = storage.load_saved_chats()

            chatName = str(chatName)
            self.currentChatName = chatName
            print(f"Current chat name is {self.currentChatName}")
            chatinfo = {
                "name" : chatName,
                "savedTime" : time.time(),
                "messages" : self.messages
            }
            freshChat = chatName in self.savedChatsDB
            self.savedChatsDB[chatName] = chatinfo

            print(f"Added messages to index {chatName}. the messages are {repr(self.messages)}")

            storage.save_chats(self.savedChatsDB)

            if not freshChat:
                self.sidebar.add(chatinfo)

            return chatName
