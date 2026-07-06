import atexit
import customtkinter as ctk

import storage
from ui.app import App

if __name__ == "__main__":
    ctk.set_appearance_mode("dark")

    app = App()
    atexit.register(lambda: storage.at_exit(app.responseDB, app.sessionInfo, app.sessionId))
    app.mainloop()
