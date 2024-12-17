import src.Data_Load
import src.Database
import src.LLM
import os
import sqlite3
import faiss
import json
from sentence_transformers import SentenceTransformer
import tkinter as tk
from tkinter import Scrollbar


def send_message():
    message = user_input.get()

    if message:
        chat_window.insert(tk.END, f"You: {message}\n", "user")
        user_input.delete(0, tk.END)

        document_string = src.Database.query_database(message, model, conn, index)

        input_text = {"input":message, "documents": document_string}

        context = context_chain.invoke(input=input_text)

        input_text = {"input":message, "context": context.content}
        response = response_chain.invoke(input=input_text)

        chat_window.insert(tk.END, response.content, "bot")
        chat_window.tag_config("user", foreground="blue")
        chat_window.tag_config("bot", foreground="green")


if __name__ == "__main__":
    
    # Load model to encode sentences
    model = SentenceTransformer('all-MiniLM-L6-v2')

    with open('config.json') as f:
        config = json.load(f)

    doc_db = config['doc_db']    
    vec_db = config['vec_db']
    download_path = config['download_path']

    # Authenticate and pull drive files
    service = src.Data_Load.authenticate_google_drive()
    print("Pulling Drive Files...")
    drive_files = src.Data_Load.pull_drive_files(service)

    # Download drive files
    print("Downloading Drive Files...")
    src.Data_Load.download_drive_files(service, drive_files, download_path)

    # Build databases
    if (os.path.exists(doc_db)):
        print("Using Existing Databases...")
        conn = sqlite3.connect(doc_db)
        index = faiss.read_index(vec_db)

    else:
        print("Building Databases...")
        conn = sqlite3.connect(doc_db)
        src.Database.setup_database(conn)
        src.Database.build_databases(download_path, conn, vec_db, model)

    context_chain, response_chain = src.LLM.create_chains()
    
    root = tk.Tk()

    root.title("Conversation")
    root.geometry("400x500")

    chat_window = tk.Text(root, bg="lightgray", height=20, width=50)
    chat_window.pack(pady=10)

    scrollbar = Scrollbar(root)
    scrollbar.pack(side="right", fill="y")
    chat_window.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=chat_window.yview)

    user_input = tk.Entry(root, width=40)
    user_input.pack(pady=5)

    send_button = tk.Button(root, text="Send", command=send_message)
    send_button.pack(pady=5)

    root.mainloop()
    