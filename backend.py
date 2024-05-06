#backend.py  Copyright (C) 2024  Valparaiso University

import time
from BackendPackage import MailController, DataRetriever

#Sender Email Address
EMAIL_ADDRESS = "photoboothreceiver@gmail.com"
#Sender Address Password
EMAIL_PASSWORD = ""
#Title of email
EMAIL_TITLE = 'Photobooth Pictures'
#Body of email
EMAIL_BODY = 'This is an email from the photobooth.\nYour pictures are attached below!'
#Url to google sheet linked with the form
SHEET_URL = "https://docs.google.com/spreadsheets/d/1YysUI-OJT6XPO9qqtwMygYJGwWc4ohH2NQ8aljmx9BI/edit?resourcekey#gid=1267535186"

#Define a GmailController
mailController = MailController(EMAIL_ADDRESS, EMAIL_PASSWORD)

#Define a DataReceiver
dataController = DataRetriever(SHEET_URL)

while True:
    time.sleep(5)
    result = dataController.checkChanges()
    if(result):
        email, folderId = dataController.getRecentData(1)
        print("Sending pictures associated with key " + folderId[0] + " to email " + email[0])
        result = mailController.sendMessage(EMAIL_TITLE, EMAIL_BODY, email[0], folderId[0])
        if(result):
            print("Pictures associated with key " + folderId[0] + " sent successfully")
        else:
            print("Pictures associated with key " + folderId[0] + " failed to send")
