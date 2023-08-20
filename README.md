# Reality Unbound
### What is this?
A text-based adventure powered by OpenAI's GPT 3.5-Turbo model. Every adventure is new and different; even the same choices entail a different story each time. Immerse and lose yourself in an endless narrative that could be curated by your dreams. Very lightweight with a clean, modern, and user-friendly interface.

# Setup 📦
### Local Machine Installation (Recommended)
Setup is easy, just follow the steps:
1. Download Python (v3.11.4+) from [here](https://www.python.org/downloads/). To check if you have it installed, run the following command
    ```
    $python --version
    ```
3. Fork and clone the repository
4. Run the following command to install all libraries
    ```
    $pip install openai customtkinter tk pillow
    ```
5. (OPTIONAL) Create a tokens.py with the following function:
    ```python
    def openAIToken():
        return "sk-..." # Enter your token in the string
    ```
    *If this step is omitted, it will prompt for a token once the app is launched. The entered token is stored locally only for the duration of the session*
7. Open cmd and change the directory to the repository folder, then run main.py using:
    ```
    $python main.py
    ```

### Replit Installation (Not recommended)
Currently, due to an issue with the Nix environment, there is unexpected behaviour on the Replit installation; there are some known issues with the Replit version:

1. The token request window does not appear if `tokens.py` is omitted
2. Popup windows not capturing priority
3. Can not clone a chat, you must create a new adventure instead

It is highly advised to use the **Local Machine** installation instead! Following are the steps to run it on Replit:
1. Fork the repository and ensure it is public
2. Go to [replit](https://www.replit.com/), log in, and press `Create Repl`
3. Import from GitHub
4. Run the following command in the shell to install all dependencies
    ```
    $pip install openai customtkinter tk pillow
    ```
5. Create a tokens.py with the following function:
    ```python
    def openAIToken():
        return "sk-..." # Enter your token in the string
    ```
    Replit will automatically ask you to turn that into a secret. Press yes, name the secret 'OpenAI Token', and refactor the code:
   ```
   import os

    def OpenAIToken():
    	return os.environ['OpenAI Token']
   ```
    *If this step is omitted, the program will refuse to open.*
7. Press on Run to test out the program :)

# Customization 🎨
There are a few things that can not be changed from the app and must be changed from within the code (found in `main.py`).
```py
    mock_data: boolean
```
Whether the application should make API calls or use mock data. 
`False` (default) means it uses API calls.

```py
    story_length_choices: int
```
This is the number of choices the GPT model is instructed to contain in the story.
*This value is only a suggestion to the language model, and should not be used as a hard cap by any means.*
Default is `10`

```py
    story_length_minutes: int
```
This is the number of minutes the GPT model is instructed to make the story.
*This value is only a suggestion to the language model, and should not be used as a hard cap by any means.*
Default is `2`

```py
    MODEL: str
```
This value determines the model that will be queried for a response. A list of models can be found [here](https://platform.openai.com/docs/models/overview/)
Default is `"gpt-3.5-turbo"`

# Known Bugs 🪰
These are some bugs I encountered during development and will look into
- Replit does not output `Token Request` window. Presumably because the `App` does not get loaded until after a token has been received
- ~~Window freezes when making API calls~~
- ~~If selected chat is deleted, it stays on screen~~
- ~~Duplicate chats clone new messages~~
- Chats do not right align properly sometimes - keeping window axis X locked for now
- `TypeError` with `NoneType` is sometimes raised when working with mock data
