import asyncio
from .models import Setting
from twilio.rest import Client
from key.twilio_creds import ACCOUNT_SID, AUTH_TOKEN
from .models import Sms
from constants import DELIVERED
from django.contrib import messages

client = Client(ACCOUNT_SID, AUTH_TOKEN)


async def send_sms(phone_number, request, msg_body):
	if phone_number:
		if len(str(phone_number)) == 0:
			pass
		else:
			if str(phone_number)[0] == '0':
				if len(phone_number) != 10:
					phone_number = str(phone_number)[1:]
					phone_number = f'+234{phone_number}'
					
					try:
						message = client.messages.create(
							to=phone_number,
							from_=str(request.tenant).upper(),
							body=msg_body)
						sms_unit = Setting.objects.first()
						sms_unit.sms_unit -= 1
						sms_unit.save()
					except:
						print("theres a problem while sending messages")