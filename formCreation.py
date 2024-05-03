#formCreation.py  Copyright (C) 2024  Valparaiso University

from googleapiclient import discovery
from oauth2client import file
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import os

SCOPES = ["https://mail.google.com/","https://www.googleapis.com/auth/drive"]

store = file.Storage("token.json")
creds = None
#If possible credentials found
if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
        token.write(creds.to_json())

service = discovery.build(
    "forms",
    "v1",
    credentials=creds
)

form = {
    "info": {
        "title": "Photobooth Photo Send Form",
        "documentTitle": "Photobooth Form",
        "description": ""
    },
}

emailQ = {
    "requests": [
        {
            "createItem": {
                "item": {
                    "title": (
                        "Please enter the email to send the pictures to:"
                    ),
                    "questionItem": {
                        "question": {
                            "required": True,
                            "textQuestion": {
                                "paragraph": False
                            },
                        }
                    },
                },
                "location": {"index": 0},
            }
        }
    ]
}

# Request body to add a multiple-choice question
photoCodeQ = {
    "requests": [
        {
            "createItem": {
                "item": {
                    "title": (
                        "Please enter the photo code that you were given:"
                    ),
                    "questionItem": {
                        "question": {
                            "required": True,
                            "textQuestion": {
                                "paragraph": False
                            },
                        }
                    },
                },
                "location": {"index": 1},
            }
        }
    ]
}


# Create form
result = service.forms().create(body=form).execute()

# Adds the question to the form
question_setting = (
    service.forms()
    .batchUpdate(formId=result["formId"], body=emailQ)
    .execute()
)
question_setting = (
    service.forms()
    .batchUpdate(formId=result["formId"], body=photoCodeQ)
    .execute()
)
print("https://docs.google.com/forms/d/" + result["formId"])