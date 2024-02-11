import base64 #standard lib
import mimetypes #standard lib
import os #standard lib
import re #standard lib
from email import encoders #standard lib
from email.mime.base import MIMEBase #standard lib
from email.mime.text import MIMEText #standard lib
from email.mime.multipart import MIMEMultipart #standard lib
import pandas as pd #pandas
from pathlib import Path #pathlib
from google.auth.transport.requests import Request #google-api-python-client
from google_auth_oauthlib.flow import InstalledAppFlow #google-api-python-client
from google.oauth2.credentials import Credentials #google-api-python-client
from googleapiclient import discovery #google-api-python-client
from oauth2client import file #oauth2client

class GmailController:
    """Functions:
        sendMessage(title, body, destEmail, folderKey, bodyFormat='plain')
    """
    def __init__(self, scopes):
        """Sets up token for google api, generates one if needed"""
        self.store = file.Storage("token.json")
        self.creds = None
        #If possible credentials found
        if os.path.exists("token.json"):
            self.creds = Credentials.from_authorized_user_file("token.json", scopes)
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", scopes
                )
                self.creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(self.creds.to_json())
        #Start gmail api service
        self.service = discovery.build("gmail", "v1", credentials=self.creds)

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
        try:
            #Grab image names in accessed image folder
            imagePath = Path('Images/') / folderKey
            images = imagePath.glob('*.*')
            images = [str(i) for i in images]
            images = list(images)
            # create email message
            message = MIMEMultipart()
            message['to'] = destEmail
            message['subject'] = title
            message.attach(MIMEText(body, bodyFormat))
            # Attach files
            for i in images:
                content_type, encoding = mimetypes.guess_type(i)
                main_type, sub_type = content_type.split('/', 1)
                f = open(i, 'rb')
                imageMIME = MIMEBase(main_type, sub_type)
                imageMIME.set_payload(f.read())
                imageMIME.add_header('Content-Disposition', 'attachment', filename=i.split("/")[-1])
                encoders.encode_base64(imageMIME)
                f.close()
                message.attach(imageMIME)
            #Encode data
            encoded_string = base64.urlsafe_b64encode(message.__bytes__()).decode()
            try:
                #Send email
                message = (self.service.users()
                    .messages()
                    .send(userId='me',body={'raw': encoded_string})
                    .execute())
                return True
            except:
                print("ERROR SENDING EMAIL")
                return False
        except:
            print("ERROR ENCODING EMAIL")
            return False

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
            folderId.append(entry[2])
        return email, folderId
