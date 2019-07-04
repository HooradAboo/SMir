import os
import pickle

import httplib2
from google_auth_oauthlib.flow import InstalledAppFlow
from oauth2client import client

from Smart_Mirror.settings import BASE_DIR
from smir.models import UserCredentials


def refresh_token(username):
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/tasks.readonly']
    creds = None
    client_id = '828422134130-bneqqft7mngj1be10i0j2ath0tl2hc9i.apps.googleusercontent.com'
    client_secret = 'ozBOZnvxR8vkoSOnh11kql0h'
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    user_creds, created = UserCredentials.objects.get_or_create(user__username=username)
    credentials = user_creds.credentials
    if credentials:
        with open(credentials, 'rb') as token:
            creds = pickle.load(token)
    else:
        credentials = os.path.join(BASE_DIR, 'tokens/{}_token.pickle'.format(user_creds.user.username))
        user_creds.credentials = credentials
        user_creds.save()
    # If there are no (valid) credentials available, let the user log in.
    if not creds:
        if creds and creds.expired and creds.refresh_token:
            creds = client.GoogleCredentials(None, client_id, client_secret,
                                             creds.refresh_token, creds.expiry,
                                             "https://accounts.google.com/o/oauth2/token", "Smart Mirror")
            http = creds.authorize(httplib2.Http())
            creds.refresh(http)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'C:/Users/asus/PycharmProjects/Smart_Mirror/smir/client_secret.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(credentials, 'wb') as token:
            pickle.dump(creds, token)
    return creds
