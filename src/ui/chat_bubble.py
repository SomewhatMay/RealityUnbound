import customtkinter as ctk

from utils import typewriter


class ChatBubble(ctk.CTkFrame):
    def __init__(self, parent, controller, role):
        super().__init__(parent)

        self.controller = controller

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
        typewriter(self.mainLabel, text, self.controller)
