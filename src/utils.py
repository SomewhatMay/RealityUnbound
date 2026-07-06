def is_empty_string(string):
    return (string == None) or (string == " ") or (string == "")


def _typewriter_help(textable, value, requiredIndex, counter=1, controller=None):
    try:
        currentIndex = textable._type_writer_index

        if not (currentIndex == requiredIndex):
            return

        textable.configure(text = value[:counter])

        try:
            if textable.is_chat_bubble == True:
                if controller is not None:
                    controller.mainWindow.messagesWindow.move_to_bottom()
                    controller.is_type_writing_response = True
        except:
            pass

        if counter < len(value):
            textable.after(6, lambda: _typewriter_help(textable, value, requiredIndex, counter + 1, controller))
        else:
            try:
                if textable.is_chat_bubble == True:
                    if controller is not None:
                        controller.is_type_writing_response = False
            except:
                pass
    except:
        if controller is not None:
            controller.is_type_writing_response = False


def typewriter(textable, value, controller=None):
    try:
        currentIndex = textable._type_writer_index
    except:
        currentIndex = 0
        textable._type_writer_index = 0

    currentIndex += 1
    textable._type_writer_index = currentIndex

    _typewriter_help(textable, value, currentIndex, controller=controller)
