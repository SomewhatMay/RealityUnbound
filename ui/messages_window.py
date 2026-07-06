import customtkinter as ctk

from ui.chat_bubble import ChatBubble


class MessagesWindow(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

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
        message_label = ChatBubble(self.scrollable_frame, self.controller, messageInfo["role"])
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
        for messageInfo in self.controller.messages:
            if messageInfo["role"] == "system":
                continue

            new_label = self.add_message(messageInfo)
            new_label.setText(messageInfo["content"]) # instantly set the text instead of animating it

        self.move_to_bottom(True)
