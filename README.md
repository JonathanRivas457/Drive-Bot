# Drive-Bot
This tool utilizes LangChain to create a custom chat bot with access to your personal google drive, allowing ChatGPT to give provide more insightful information regarding you own documents. 

# Installation
Insallation instructions involves acquiring google cloud authentication as well as setting up environment variables for the program to access

## Install Dependencies
To install all necessary libraries, run the command
```pip install -r requirements.txt```

## Google Cloud
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project.
3. Enable the Google Drive API in the API Library.
4. Create OAuth 2.0 credentials under the "Credentials" tab.
5. Download the credentials as a credentials.json file.
6. Move the credentials.json file to your project directory.
7. Install Google client libraries (inclued in requirements.txt)
8. store 'credentials.json' in 'data' folder

## .env and config
in the .env file you will follow the format
GOOGLE_CREDENTIALS="data/credentials.json"
OPENAI_KEY="YOUR-KEY"

in the config file you will follow the format
{
    "doc_db": "data/DocumentDatabase.db",
    "vec_db": "data/VectorDatabase.index",
    "download_path": "data/Drive_Files"
}

## Execution
Run the command ```python main.py``` to execute the program
The program will ask for access to your drive and then download all files from the drive 
Once downloaded the program will create a Chat UI which you will be able to communicate with the personalized chatbot
