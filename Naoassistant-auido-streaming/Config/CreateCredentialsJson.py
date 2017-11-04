import json

# ADD YOUR CREDENTIALS IN HERE, ENSURE YOU ADD YOUR CREDENTIALS TO THE CORRECT
# REGION. USE CORRECT SYNTAX - SEE EXAMPLE BELOW:

# NLC = {
#     "url": "https://stream.watsonplatform.net/speech-to-text/api",
#     "password": "xxxxxxxxxxx",
#     "username": "xxxxxxxxxx-xxxxxxxxxxx-xxxxxxxxxx-xxxxxxxxxxx"
# }
# VR = {
#     "url": "https://gateway-a.watsonplatform.net/visual-recognition/api",
#     "api_key": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
#     "version": '2016-05-20'
# }

# Australia credentials
AusNLC = {
}
AusSpeechToText = {
}
AusVR = {
}
AusConversation = {
}
# US South credentials
USNLC = {
  "url": "https://gateway.watsonplatform.net/natural-language-classifier/api",
  "username": "b045eb25-5309-4a2c-b191-afb58128beb4",
  "password": "TetdhkshOOsl"
}
USConversation = {
  "url": "https://gateway.watsonplatform.net/conversation/api",
  "username": "370913eb-22d2-42cd-bc23-4ea1b4d6900d",
  "password": "I3BK8LTLS6DD",
 # "ID": "1f247258-be1e-4f7b-97ba-fde1711d7efd" version 1
  "ID": "5ff68f15-f999-408d-97d2-dbf5f2747110"

}
USSpeechToText = {"url": "https://stream.watsonplatform.net/speech-to-text/api",
  "username": "34639a58-279e-4f9a-a3cc-7ba6a8f3bd54",
  "password": "hiMG5kNzPHY1"
}
USVR = {
  "url": "https://gateway-a.watsonplatform.net/visual-recognition/api",
  "note": "It may take up to 5 minutes for this key to become active",
  "api_key": "df496f2c2ff054af344b37384ee01dae66e6323e",
  "version": "2016-05-20"
}

#~-~ ~-~ ~-~ ~-~ ~-~ ~-~ ~-~ ~-~ ~-~ ~-~ ~-~ ~-~ ~-~ ~-~ ~-~ ~-~ ~-~ ~-~ ~-~ ~-#
# DO NOT MODIFY CODE BELOW THIS LINE


Australia = {
"NLC": AusNLC,
"Conversation": AusConversation,
"SpeechToText": AusSpeechToText,
"VisualRecognition": AusVR
}
USSouth = {
"NLC": USNLC,
"Conversation": USConversation,
"SpeechToText": USSpeechToText,
"VisualRecognition": USVR
}

data = {}
data["region"] = {}
data["region"]["Australia"] = {}
data["region"]["EE.UU.sur"] = {}

data["region"]["Australia"] = Australia
data["region"]["EE.UU.sur"] = USSouth

with open('credentials.json', 'w') as outfile:
    json.dump(data, outfile, indent=2)

with open('credentials.json') as outfile:
    print json.dumps(json.load(outfile), indent=2, sort_keys=True)

print "Credentials saved."
