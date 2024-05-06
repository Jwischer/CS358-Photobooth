#backendClasses.py  Copyright (C) 2024  Valparaiso University

import smtplib, ssl
import mimetypes #standard lib
import os #standard lib
import re #standard lib
from email import encoders #standard lib
from email.mime.base import MIMEBase #standard lib
from email.mime.text import MIMEText #standard lib
from email.mime.multipart import MIMEMultipart #standard lib
import pandas as pd #pandas
from pathlib import Path #pathlib

class MailController:
    """Functions:
        sendMessage(title, body, destEmail, folderKey, bodyFormat='plain')
    """
    def __init__(self, email, password):
        self.email = email
        self.password = password
        pass

    def sendMessage(self, title, body, destEmail, folderKey, bodyFormat='plain'):
        """Sends a email using gmail to destEmal, containing files in folder Images/folderKey

            title: title of email
            body: body of email
            destEmail: email address to send the email to
            folderKey: name of folder the pictures you want to send are stored in
                relative path to attachments should be Images/folderKey with all attachments inside folder folderKey
            bodyFormat: text format the body is in, plain by default
            Returns: bool (True if successfully sent, False if not)
        """
        #try:
        #Grab image names in accessed image folder
        imagePath = sorted((Path('Images') / folderKey).iterdir(), key = os.path.getmtime)
        #images = imagePath.glob('*.*')
        images = [str(i) for i in imagePath]
        images = list(images)
        print(images)

        # Create a multipart message and set headers
        message = MIMEMultipart()
        message["From"] = self.email
        message["To"] = destEmail
        message["Subject"] = title
        # Add body to email
        message.attach(MIMEText(body, "plain"))

        # Attach files
        for i in images:
            # Open file in binary mode
            with open(i, "rb") as attachment:
                # Add file as application/octet-stream
                # Email client can usually download this automatically as attachment
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            # Encode file in ASCII characters to send by email    
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            part.add_header(
                "Content-Disposition",
                f"attachment; filename= {i.split('/')[-1]}",
            )

            # Add attachment to message and convert message to string
            message.attach(part)
        #Convert message to a string
        text = message.as_string()

        #try:
        #Send email
        context=ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(self.email, self.password)
            server.sendmail(self.email, destEmail, text)
        return True
            #except:
             #   print("ERROR SENDING EMAIL")
             #   return False
       # except:
       #     print("ERROR ENCODING EMAIL")
       #     return False

class DataRetriever:
    """Checks if there are changes to a given google sheet and gets data from a given google sheet
    
        Functions:
        checkChanges()
        getRecentData(num)
    """
    def __init__(self, sheetsUrl):
        """Inititalizes dataRetreiver with given link to public google sheet"""
        # Regular expression to match and capture the necessary part of the URL
        pattern = r'https://docs\.google\.com/spreadsheets/d/([a-zA-Z0-9-_]+)(/edit#gid=(\d+)|/edit.*)?'
        # Replace function to construct the new URL for CSV export
        # If gid is present in the URL, it includes it in the export URL, otherwise, it's omitted
        downloadUrl = lambda m: f'https://docs.google.com/spreadsheets/d/{m.group(1)}/export?' + (f'gid={m.group(3)}&' if m.group(3) else '') + 'format=csv'
        # Replace using regex
        downloadUrl = re.sub(pattern, downloadUrl, sheetsUrl)
        #Store csv download link
        self.csvUrl = downloadUrl
        self.currentData = pd.read_csv(self.csvUrl)

    def checkChanges(self):
        """Checks to see if any changes have been made to the data retriever website

            Returns: bool (True if different, False otherwise)
        """
        #Get frame and compare
        df2 = pd.read_csv(self.csvUrl)
        #If no change
        if(self.currentData.equals(df2)):
            return False
        #Change detected
        else:
            #Update currentData with new data
            self.currentData = df2
            return True

    def getRecentData(self, num):
        """Retrieves the most recent num entries from current dataframe

            Returns: email (list of emails), folderKey (list of folder keys)
                email and folderKey lists are ordered by most recent response
        """
        email = []
        folderId = []
        for i in range(num):
            entry = self.currentData.iloc[-(i+1)]
            entry = entry.values.tolist()
            email.append(entry[1])
            folderId.append(entry[2].upper())
        return email, folderId
