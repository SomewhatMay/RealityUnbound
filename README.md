# Setup 📦
For some reason, Replit is causing issues with displaying window popups (save chat window, new chat window, etc); **I highly suggest running this locally.** Setup is easy, just follow the steps:
1. Ensure that you have Python (v3.11.4) installed
2. Fork and clone the repository
3. Run the following command to install all libraries
    ```
        $pip install openai customtkinter tk pillow
    ```
4. (OPTIONAL) Create a tokens.py with the following function:
    ```python
        def openAIToken():
            return "sk-..." # Enter your token in the string
    ```
    *This step is only required if you are running from [replit](https://www.replit.com/). If omitted, it will prompt for a token once the app is launched. The entered token is stored locally only for the duration of the session*
5. Run main.py:
    ```
        $python main.py
    ```

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
