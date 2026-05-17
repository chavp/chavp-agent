from dotenv import load_dotenv
import os

from fastapi import FastAPI, Query

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader

import chromadb
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings

load_dotenv() #A
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") #B
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "64"))

app = FastAPI(
    title="พระไตรปิฎก",
    description="API พระไตรปิฎก",
    version="1.0.0",
    terms_of_service="https://chavp.wordpress.com/about/",
    contact={
        "name": "ทีมพัฒนาซอฟต์แวร์",
        "url": "https://chavp.wordpress.com",
        "email": "my.parinya@gmail.com",
    },
)

def get_vec_db(api_key, batch_size):
    client = chromadb.HttpClient(host="http://localhost:8010")
    vector_db = Chroma(
        client=client,
        collection_name="tripitaka_collection",
        embedding_function=OpenAIEmbeddings(
            openai_api_key=api_key,
            chunk_size=batch_size,
        )
    )
    return vector_db

def split_and_import(loader, vec_db, text_splitter):
     chunks = text_splitter.split_documents(loader.load())
     vec_db.add_documents(chunks)
     print(f"Ingested chunks created by {loader}")

loader_classes = {
    'docx': Docx2txtLoader,
    'pdf': PyPDFLoader,
    'txt': TextLoader
}
def get_loader(filename):
    _, file_extension = os.path.splitext(filename) #A Extract the file extension
    file_extension = file_extension.lstrip('.') #B Remove the leading dot from the extension
    
    loader_class = loader_classes.get(
        file_extension) #C Get the loader class from the dictionary
    
    if loader_class:
        return loader_class(filename) #D Instantiate and return the correct loader
    else:
        raise ValueError(f"No loader available for file extension '{file_extension}'")


@app.put("/load-path", tags=["buddha-agent"], summary="พระไตรปิฎก", description="lโหลดข้อมูลพระไตรปิฎก")
def load_path(file_path: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    
    pdf_loader = PyPDFLoader(file_path)
    pdf_chunks = text_splitter.split_documents(pdf_loader.load())

    vector_db = get_vec_db(OPENAI_API_KEY, EMBEDDING_BATCH_SIZE)
    vector_db.add_documents(pdf_chunks)

    return {"message": "Load completed"}

@app.put("/load-folder", tags=["buddha-agent"], summary="พระไตรปิฎก", description="lโหลดข้อมูลพระไตรปิฎก")
def load_folder(folder: str):
    vector_db = get_vec_db(OPENAI_API_KEY, EMBEDDING_BATCH_SIZE)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=0)
    for filename in os.listdir(folder): #B iterate over the files in the path
        file_path = os.path.join(folder, filename) #C Construct the full path to the file
    
        if os.path.isfile(file_path): #D Check if it is a file (not a directory)
            try:
                loader = get_loader(file_path) #E Instantiate the correct loader for the file
                print(f"Loader for {filename}: {loader}")
                split_and_import(loader, vector_db, text_splitter) #F Split and ingest
            except ValueError as e:
                print(e)

    return {"message": "Load completed"}