from twilio.rest import Client


# Your Account Sid and Auth Token from twilio.com/console
# DANGER! This is insecure. See http://twil.io/secure
account_sid = 'ACac30a3c0cd50996f60e6b0d56d019922'
auth_token = 'd815b7a87b5c8556c123a8af251aeb43'
client = Client(account_sid, auth_token)

message = client.messages \
                .create(
                     body="Join Earth's mightiest heroes. Like Kevin Bacon.",
                     from_='Bitpoint',
                     to='+919725093227'
                 )

print(message.sid)