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
USNLC = {"url": "https://gateway.watsonplatform.net/natural-language-classifier/api",
  "username": "5297a718-5ea1-4eb3-9f60-55a13add20a0",
  "password": "e8plhQMYem7k"
}
USConversation = {"url": "https://gateway.watsonplatform.net/conversation/api",
  "username": "55428ee7-07a6-4fc9-b50e-16e777c55757",
  "password": "CnfqyNKOmFRo"
}
USSpeechToText = {"url": "https://stream.watsonplatform.net/speech-to-text/api",
  "username": "34639a58-279e-4f9a-a3cc-7ba6a8f3bd54",
  "password": "hiMG5kNzPHY1"
}
USVR = {"url": "https://gateway-a.watsonplatform.net/visual-recognition/api",
  "note": "This is your previous free key. If you want a different one, please wait 24 hours after unbinding the key and try again.",
  "api_key": "b6b09f1f65a125a79343b7a03f14b7418dd0dcf1",
  "version": '2016-05-20'
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
data["region"]["US South"] = {}

data["region"]["Australia"] = Australia
data["region"]["US South"] = USSouth

with open('credentials.json', 'w') as outfile:
    json.dump(data, outfile, indent=2)

with open('credentials.json') as outfile:
    print json.dumps(json.load(outfile), indent=2, sort_keys=True)

print "Credentials saved."
