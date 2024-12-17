import os
import re
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import io
from tqdm import tqdm
from googleapiclient.http import MediaIoBaseDownload
from dotenv import load_dotenv

load_dotenv()

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def authenticate_google_drive():
    creds = None
    # The file token.pickle stores the user"s access and refresh tokens
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                os.getenv("GOOGLE_CREDENTIALS"), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    
    return build("drive", "v3", credentials=creds)


def clean_file_name(file_name):

    cleaned_name = re.sub(r'[\/:*?"<>|.]', '_', file_name)

    return cleaned_name


def pull_drive_files(service):

    # List to store file data
    all_files = []

    # Initial query (file name, id, type, and nextPage)
    results = service.files().list(
        q="mimeType='application/vnd.google-apps.document' or mimeType='application/pdf' or mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'",
        pageSize=20, 
        fields="nextPageToken, files(id, name, mimeType)"
        ).execute()
    
    items = results.get("files", [])

    all_files.extend(items)

    # Continue querying until we've pull all the files
    while results.get('nextPageToken') != None:

        # Pull next set of files starting at the last page
        results = service.files().list(
            q="mimeType='application/vnd.google-apps.document' or mimeType='application/pdf' or mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document'",
            pageSize=20, 
            fields="nextPageToken, files(id, name, mimeType)", 
            pageToken=results["nextPageToken"]
            ).execute()
        
        items = results.get("files", [])
        all_files.extend(items)
    
    print(f"{len(all_files)} files pulled")

    return all_files


def download_drive_files(service, drive_files, download_path):
    
    error_files = []

    # Create directory if doesn't exist
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # Iterate through each file 
    for file in tqdm(drive_files, desc="Downloading Files...", ncols=100):

        file_type = file['mimeType']

        # Construct query based on file type
        if file_type == "application/vnd.google-apps.document":

            file_name = clean_file_name(file['name']) + '.docx'  # Clean file name
            file_path = os.path.join(download_path, file_name)
            
            # Skip if file already exists
            if os.path.exists(file_path):
                continue

            request = service.files().export_media(
                fileId=file['id'],
                mimeType="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        elif file_type == "application/pdf":

            file_name = file['name'] + '.pdf'
            file_path = os.path.join(download_path, file_name)

            # Skip if file already exists
            if os.path.exists(file_path):
                continue

            request = service.files().get_media(
                fileId=file['id']
            )

        else:
            
            file_name = file['name'] + '.docx'
            file_path = os.path.join(download_path, file_name)

            # Skip if file already exists
            if os.path.exists(file_path):
                continue

            request = service.files().get_media(
                fileId=file['id']
            )


        # Download file
        fh = io.FileIO(file_path, 'wb')
        try:
            downloader = MediaIoBaseDownload(fh, request)
            done = False

            while done is False:
                status, done = downloader.next_chunk()  

        except Exception as e:
            error_files.append(file['name'])

    print(f"Failed to download the following files: {error_files} \n Please try downloading them manually")

    return
