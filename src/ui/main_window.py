import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk

from utils import is_empty_string, typewriter
from ui.messages_window import MessagesWindow


class MainWindow(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color = "transparent")

        self.controller = controller

        self.grid(column = 3, row = 1, sticky = "nswe", padx = (0, 10), pady = 10)

        # Menu screen

        startAdventureButton = ctk.CTkButton(
            self,
            text = "Begin New Adventure",
            command = lambda: self.controller.newChat()
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

        messagesWindow = MessagesWindow(self, self.controller)

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

        self.in_menu_screen = False
        self.menuScreen()

    def sendMessage(self):
        if (self.controller.is_loading_chat == True) or (self.controller.is_querying == True) or (self.controller.is_type_writing_response == True):
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

        userMessage = self.controller.newMessage(messageInfo)
        userMessage.setText(messageContent)
        self.messagesWindow.move_to_bottom()

        self.controller.saveChat(self.controller.currentChatName)

        self.controller.makeCompletion()

    def menuScreen(self):
        self.in_menu_screen = True
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
        self.chatBox.place(relx = 2)
        self.sendButton.place(relx = 2)

    def chatScreen(self):
        self.in_menu_screen = False
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
