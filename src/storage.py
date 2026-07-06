import json


def load_responses():
    with open("responses.json", "r") as responseJson:
        return json.load(responseJson)


def load_mock_responses():
    with open("mockResponses.json", "r") as mockresponsesJson:
        return json.load(mockresponsesJson)


def load_saved_chats():
    with open("savedChats.json", "r") as savedChatsJson:
        return json.load(savedChatsJson)


def save_chats(db):
    with open("savedChats.json", "w") as savedChatsJson:
        json.dump(db, savedChatsJson, indent=4)


def save_mock_responses(db):
    with open("mockResponses.json", "w") as mockresponsesJson:
        json.dump(db, mockresponsesJson, indent=4)


def save_responses(db):
    with open("responses.json", "w") as responseJson:
        json.dump(db, responseJson, indent=4)


def at_exit(responseDB, sessionInfo, sessionId):
    if len(sessionInfo["responses"]) > 0:
        responseDB["tokenUsage"]["outbound"] += sessionInfo["tokenUsage"]["outbound"]
        responseDB["tokenUsage"]["inbound"] += sessionInfo["tokenUsage"]["inbound"]
        responseDB["sessions"][sessionId] = sessionInfo

        save_responses(responseDB)
