import africastalking
from key.africastalking import USERNAME, API_KEY
from sms_notification.models import Setting
from .models import Setting

class SMS:
    def __init__(self):
        africastalking.initialize(USERNAME, API_KEY)
        self.sms = africastalking.SMS

    def send(self, message, recipients):
            sender = Setting.objects.first().sender_id
            if recipients:
                try:
                    response = self.sms.send(message, recipients, sender)
                    print (response)
                    unit = Setting.objects.first()
                    unit.available_unit -= 1
                    unit.save()
                except Exception as e:
                    print ('Encountered an error while sending: %s' % str(e))
            else:
                print('No recipients')
if __name__ == '__main__':
    SMS().send()