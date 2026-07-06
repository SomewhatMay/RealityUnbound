import copy
import customtkinter as ctk

import storage
from prompts import deafult_messages
from ui.dialogs import ConfirmDialog


class Sidebar(ctk.CTkScrollableFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

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
            command = lambda: self.controller.loadByName(chatInfo["name"])
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

        self.controller.wait_window(ConfirmDialog(self.controller, "Confirm Delete", "Are you sure you want to delete this save?", delete_callback))

    def remove(self, chatInfo, button):
        if self.controller.currentChatName == chatInfo["name"]:
            self.controller.mainWindow.messagesWindow.unload_messages()
            self.controller.messages = copy.deepcopy(deafult_messages)
            self.controller.currentChatName = self.controller.sessionId
            self.controller.mainWindow.menuScreen()

        button.destroy()
        self.controller.savedChatsDB.pop(chatInfo["name"])

        storage.save_chats(self.controller.savedChatsDB)

    def loadAll(self):
        for chatName in self.controller.savedChatsDB:
            chatInfo = self.controller.savedChatsDB[chatName]
            self.add(chatInfo)
