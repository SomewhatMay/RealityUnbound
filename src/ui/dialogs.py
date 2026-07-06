import copy
import time
import customtkinter as ctk

from prompts import deafult_messages
from utils import is_empty_string


class ConfirmDialog(ctk.CTkToplevel):
    def __init__(self, controller, titleText, confirmText, callback):
        super().__init__(controller)

        self.controller = controller

        self.title(titleText)
        self.transient(controller)
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


class NewJourneyWindow(ctk.CTkToplevel):
    def __init__(self, controller):
        super().__init__()

        self.controller = controller

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

        newMessages[0]["content"] += " Please begin by explaining and introducing the game to the player and the current setting (with choices)."

        chatInfo = {
            "name": newChatName,
            "savedTime": time.time(),
            "messages": newMessages
        }

        self.controller.saveChat(newChatName)
        chatInfo["name"] = self.controller.currentChatName
        self.controller.loadChat(chatInfo)
        self.destroy()

        self.controller.makeCompletion()
