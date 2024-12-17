import pdfplumber
import docx
import os
import faiss
import numpy as np
from tqdm import tqdm
import sqlite3

# Function to read a docx file
def read_docx(file_path):
    text = ""
    try:
        doc = docx.Document(file_path)

        for paragraph in doc.paragraphs:

            text += paragraph.text + "\n"

    except Exception as e:
        return text

    return text


# Function to read a pdf file
def read_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:

            text = ""

            for page in pdf.pages:

                text += page.extract_text()

    except Exception as e:
        return text

    return text


# Function to setup database
def setup_database(conn):

    cursor = conn.cursor()

    # Create document table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS document (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT,
            content TEXT,
            vector_index INTEGER
            )
    ''')

    # Commit changes
    conn.commit()


# Function to build databases
def build_databases(file_directory, conn, vec_db, model):

    # Create cursor
    cursor = conn.cursor()

    # Create index (vector database)
    dimension = 384
    index = faiss.IndexIDMap(faiss.IndexFlatL2(dimension))
    curr_id = 0

    # Go through drive files
    file_list = os.listdir(file_directory)
    for file in tqdm(file_list, desc="Processing files", unit="file"):

        # Construct file path and names
        file_path = file_directory + "/" + file
        filename = file_path.split('/')[-1]

        
        # Read text from files
        if (file.endswith(".docx")):
            text = read_docx(file_path)

        elif (file.endswith(".pdf")):
            text = read_pdf(file_path)

        # Encode text if file is not empty
        if text != "":
            encoded_text = model.encode(text)
            encoded_text = encoded_text.reshape(1, -1)

            # Add document and encodeded text
            cursor.execute("INSERT INTO document (filename, content, vector_index) VALUES (?, ?, ?)", (filename, text, curr_id))
            index.add_with_ids(encoded_text, np.array([curr_id]))

        curr_id += 1

    # Commit changes and save vector database    
    conn.commit()
    faiss.write_index(index, vec_db)

    return


def query_database(prompt, model, conn, index):
    cursor = conn.cursor()

    encoded_prompt = model.encode(prompt)
    encoded_prompt = encoded_prompt.reshape(1, -1)

    k = 3

    distances, indices = index.search(encoded_prompt, k)
    indices = indices[0]
    results = []

    context_string = ""

    for iteration, index in enumerate(indices, start=1):
        document_string = ""
        cursor.execute("SELECT filename, content FROM document WHERE vector_index = ?", (int(index),))
        result = cursor.fetchall()[0]
        filename = result[0]
        content = result[1]

        document_string = f"Document{iteration} \n    FileName: {filename} \n    content: {content}"
        context_string += document_string + "\n"


    return context_string


