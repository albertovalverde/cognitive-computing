# #from twilio.rest import Client
#
# from twilio import client
#
#
# # Your Account SID from twilio.com/console
# account_sid = "AC2815564b118b8d4d248f5145dcc4bffe"
# # Your Auth Token from twilio.com/console
# auth_token  = "dfc343ad74ace899670b5b7684e932aa"
#
# client2 = client(account_sid, auth_token)
#
# message = client2.messages.create(
#     to="+34608837254",
#     from_="+15017250604",
#     body="Hello from Python!")
#
# print(message.sid)


# /usr/bin/env python
# Download the twilio-python library from http://twilio.com/docs/libraries


from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = "ACdc086b7edc7e003e1b8255fdd7f85445"
# Your Auth Token from twilio.com/console
auth_token  = "0eb7554e13abf88ae162f6eb2cd5407c"

client = Client(account_sid, auth_token)

message = client.messages.create(
    to="+34608837254",
    from_="+12564748504",
    body="Hola soy Nao! estoy haciendo unas pruebas")

print(message.sid)