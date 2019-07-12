import asyncio
from twilio.rest import Client
from .twilio_token import ACCOUNT_SID, AUTH_TOKEN


client = Client(ACCOUNT_SID, AUTH_TOKEN)


async def send_sms(phone, msg):
	if phone:
		if len(str(phone)) == 0:
			pass
		else:
			if str(phone)[0] == '0':
				if len(phone) != 10:
					phone = str(phone)[1:]
					phone = '+234{}'.format(phone)
					try:
						message = client.messages.create(
							to=phone,
							from_='Bitpoint inc.',
							body=msg
						)
						print("message send with an ID of {}".format(message.sid))
					except:
						print("theres an error while sending sms")