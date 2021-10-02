from twilio.rest import Client

account_sid = 'AC243a73467bfb2ad374207e7f7c'
auth_token = '[AuthToken]'
client = Client(account_sid, auth_token)

message = client.messages.create(
    messaging_service_sid='+18923893928',
    body='You are in an immediate danger position. The fire will probably invade this area within 12 hours. '
         'We highly suggest you to move towards the south-west direction.  '
         'For getting help: Fire-Fighter: 01816362728 Ranger: 938272637281   '
         'Thanks for using firefly web-app which is always dedicated to save your life.',
    to='+8801746695655'
)

print(message.sid)