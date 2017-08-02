from watson_developer_cloud import ConversationV1
import json

class Conversation:
    def __init__(self, workspace):
        self.conversation = ConversationV1(
            username='', # Credentials
            password='',
            version='2016-07-11')
        self.workspaceId = "" # Workspace ID
        self.conversationID = "qwerty"
        self.dialog_turn_counter = 1
        self.dialog_request_counter = 1
        self.dialog_stack = "root"

    def response(self, userInput):
        responseJson = self.conversation.message(workspace_id=self.workspaceId, message_input={'text': userInput}, context={'conversation_id': self.conversationID, 'system': {'dialog_stack': [self.dialog_stack],'dialog_turn_counter': self.dialog_turn_counter,'dialog_request_counter': self.dialog_request_counter}})

        self.dialog_turn_counter = responseJson["context"]["system"]["dialog_turn_counter"]
        self.dialog_request_counter = responseJson["context"]["system"]["dialog_request_counter"]
        self.dialog_stack = responseJson["context"]["system"]["dialog_stack"][0]
        # print "Turn counter:", self.dialog_turn_counter, "- " + "Request counter:", self.dialog_request_counter, ""
        # print json.dumps(responseJson, sort_keys=True, indent=4, separators=(',', ': '))

        intent = responseJson["intents"][0]["intent"]

        try:
            response = responseJson["output"]["text"][0]
        except:
            response = "Woops, I don't know the answer to that right now!"
        try:
            nodeId = responseJson["output"]["NODEID"]
        except:
            nodeId = None

        return [response, intent]
