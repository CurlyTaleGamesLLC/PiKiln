import smtplib
import json
# import time
from datetime import datetime
import pytz

def SendEmail(sender, senderPassword, receiver, emailSubject, emailContent, tzone):
    # Establish connection to GMAIL
    conn = smtplib.SMTP('imap.gmail.com',587)
    conn.ehlo()
    conn.starttls()
    conn.login(sender, senderPassword)

    # current date and time
    nowTime = datetime.now(tz=pytz.timezone(tzone))
    timestamp = nowTime.strftime("%Y-%m-%d %H:%M:%S")
    print (timestamp)

    # Create Message
    message = 'Subject: ' + emailSubject + " " + timestamp + '\n\n ' + emailContent

    # Send Email, and close connection
    conn.sendmail(sender, receiver, message)
    conn.quit()

def Send(emailSubject, emailContent):
    print("reading settings.json")
    with open('settings.json') as json_file:
        data = json.load(json_file)

        # Load Settings
        emailEnabled = data['notifications']['enable-email']
        sender = data['notifications']['sender']
        senderPassword = data['notifications']['sender-password']
        receiver = data['notifications']['receiver']
        tzone = data['notifications']['timezone']

        # print(emailEnabled)
        # print(sender)
        # print(senderPassword)
        # print(receiver)
        # print(tzone)

        if emailEnabled:
            SendEmail(sender, senderPassword, receiver, emailSubject, emailContent, tzone)


Send("Bisque Fire Complete!", "You've got bisqueware waiting for you in your kiln :)")


# pi.kiln.notification@gmail.com
# NeverGonnaGiveYouUp!1

# https://www.google.com/settings/security/lesssecureapps
# https://accounts.google.com/DisplayUnlockCaptcha