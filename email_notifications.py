import requests
import os
import io
import datetime
import pytz

import settings



# JSON for complete.html
# emailJSON = {
#     "subject":"White Crackle Glaze 07 - Firing Complete!",
#     "schedule":"White Crackle Glaze 07",
#     "duration":"3:40",
#     "cost":"$3.50"
# }

# JSON for self-check-error.html
# emailJSON = {
#     "subject":"Self Check Error"
# }

# JSON for max-temp-error.hmtl
# emailJSON = {
#     "subject":"Max Temperature Error"
# }

def GetTimestamp():
    # tzone = pytz.timezone(settings.settings['notifications']['timezone'])
    nowTime = datetime.datetime.now()
    nowTimeFormat = nowTime.strftime("%Y-%m-%d %H:%M:%S")
    print(nowTimeFormat)
    return nowTimeFormat

def ReplaceParameter(baseString, parameter, content):
    return baseString.replace("{{" + parameter + "}}", content)

def EmailContent(contentPath, contentJSON):
    
    basePath = os.path.join('email', "email.html")
    fullPath = os.path.join('email', contentPath)

    # loads base email template
    with open(basePath, 'r') as f:
        baseEmailTemplate = f.read()

    # loads content for email template
    with open(fullPath, 'r') as f:
        templateContent = f.read()

    message = ReplaceParameter(baseEmailTemplate, "content", templateContent)

    # Replaces all {{items}} in email with data from JSON 
    for key, value in contentJSON.items():
        message = ReplaceParameter(message, key, value)

    # print(message)
    return message

# Sends email to receiver
def SendEmail(contentPath, contentJSON):
    print("Send Email?")
    if settings.settings['email'] != "":
        print("Sending Email")
        url = "https://p44f20evs1.execute-api.us-east-1.amazonaws.com/Production/send"

        emailObject = {
            "toEmail": settings.settings['email'],
            "subject": contentJSON['subject'] + " " + GetTimestamp(),
            "message": EmailContent(contentPath, contentJSON)
        }
        requests.post(url, json = emailObject)
        print("Email Sent")
        # return requests.post(url, json = myobj).text