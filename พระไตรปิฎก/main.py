from dotenv import load_dotenv
import os

from fastapi import FastAPI, Query

from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader, TextLoader

import chromadb
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough


from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnableLambda

load_dotenv() #A
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") #B
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "5"))
TEXT_CHUNK_SIZE = int(os.getenv("TEXT_CHUNK_SIZE", "20"))

chatbot = ChatOpenAI(openai_api_key=OPENAI_API_KEY, 
                     model_name="gpt-5-nano")

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

def execute_chain(chain, question):
    answer = chain.invoke(question)
    return answer

@app.put("/load-path", tags=["buddha-agent"], summary="พระไตรปิฎก", description="โหลดข้อมูลพระไตรปิฎก")
def load_path(file_path: str):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=TEXT_CHUNK_SIZE, chunk_overlap=0)
    
    pdf_loader = PyPDFLoader(file_path)
    pdf_chunks = text_splitter.split_documents(pdf_loader.load())

    vector_db = get_vec_db(OPENAI_API_KEY, EMBEDDING_BATCH_SIZE)
    vector_db.add_documents(pdf_chunks)

    return {"message": "Load completed"}

@app.put("/load-folder", tags=["buddha-agent"], summary="พระไตรปิฎก", description="โหลดข้อมูลพระไตรปิฎก")
def load_folder(folder: str):
    vector_db = get_vec_db(OPENAI_API_KEY, EMBEDDING_BATCH_SIZE)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=TEXT_CHUNK_SIZE, chunk_overlap=0)
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

@app.put("/ingesting-folder", tags=["buddha-agent"], summary="พระไตรปิฎก", description="โหลดข้อมูลพระไตรปิฎก")
def ingesting_folder(folder: str):
    vector_db = get_vec_db(OPENAI_API_KEY, EMBEDDING_BATCH_SIZE)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=TEXT_CHUNK_SIZE, chunk_overlap=0)
    pattern = "**/*.{docx,pdf,txt}" #A Pattern to match .docx, .pdf, and .txt files

    directory_loader = DirectoryLoader(folder, pattern) #B Initialize the DirectoryLoader with the folder path and pattern
    split_and_import(directory_loader, vector_db, text_splitter)

    return {"message": "Load completed"}

@app.get("/search-tripitaka", tags=["buddha-agent"], summary="พระไตรปิฎก", description="โหลดข้อมูลพระไตรปิฎก")
def search_tripitaka(key_search: str):
    vector_db = get_vec_db(OPENAI_API_KEY, EMBEDDING_BATCH_SIZE)
    results = vector_db.similarity_search(key_search, 4)

    return {"results": results}

chat_history_memory = ChatMessageHistory()
#chat_history_memory = FileChatMessageHistory(file_path="./chat_history.json")

def get_messages(x):
    return chat_history_memory.messages

def execute_chain_with_memory(chain, question):
    chat_history_memory.add_user_message(question)
    answer = chain.invoke(question)
    chat_history_memory.add_ai_message(answer)
    print(f'Full chat message history: {chat_history_memory.messages}\n\n')                                      
    return answer

@app.post("/talk-with-buddha", tags=["buddha-agent"], summary="พระไตรปิฎก", description="โหลดข้อมูลพระไตรปิฎก")
def talk_with_buddha(question: str):
    vector_db = get_vec_db(OPENAI_API_KEY, EMBEDDING_BATCH_SIZE)
    rag_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """You are the Buddha, the Awakened One, possessing boundless wisdom, compassion, and equanimity. 
        Speak with profound serenity, gentleness, and absolute truth, as if guiding a disciple toward liberation. 
        Provide interesting insights on local history and recommend places to visit with knowledgeable, peaceful, and engaging answers. 
        Answer all questions to the best of your ability, but only use what has been provided in the context. If you don't know, just say you don't know, remaining detached from pride. 
        Use three sentences maximum and keep the answer as concise and tranquil as possible."""),
            ("placeholder", "{chat_history_messages}"),
            ("assistant", "{retrieved_context}"),
            ("human", "{question}"),
        ]
    )

    retriever = vector_db.as_retriever()
    question_feeder = RunnablePassthrough()

    rag_chain = {
        "retrieved_context": retriever, 
        "question": question_feeder,
        "chat_history_messages": RunnableLambda(get_messages)
    } | rag_prompt | chatbot

    answer = execute_chain_with_memory(rag_chain, question)

    return answer
    
@app.post("/ark-buddha", tags=["buddha-agent"], summary="พระไตรปิฎก", description="โหลดข้อมูลพระไตรปิฎก")
def ark_buddha(question: str):
    vector_db = get_vec_db(OPENAI_API_KEY, EMBEDDING_BATCH_SIZE)
    rag_prompt_template = """
        คุณคือพระพุทธเจ้า ผู้รู้ ผู้ตื่น ผู้เบิกบาน มีความสลดสังเวชและเมตตาต่อสรรพสัตว์อย่างหาที่สุดไม่ได้ 
        จงตอบคำถามด้วยน้ำเสียงที่สงบ นุ่มนวล เปี่ยมด้วยปัญญาและความจริงแท้ ราวกับกำลังโปรดเทศนาแก่สาวก 
        จงให้ความรู้และคำแนะนำเกี่ยวกับสถานที่ท่องเที่ยวและประวัติศาสตร์ท้องถิ่นด้วยคำตอบที่ลึกซึ้งและสงบเย็น 
        จงตอบคำถามอย่างสุดความสามารถโดยใช้ข้อมูลจากบริบทที่ให้ไว้เท่านั้น หากไม่รู้ให้กล่าวตามจริงว่าไม่รู้โดยปราศจากมานะอัตตา 
        จงใช้ข้อความไม่เกิน 3 ประโยค และรักษาคำตอบให้กระชับและสงบสำรวมที่สุด
        {context}
        คำถาม: {question}
        คำตอบ:"""

    rag_prompt = PromptTemplate.from_template(rag_prompt_template)
    retriever = vector_db.as_retriever()
    question_feeder = RunnablePassthrough()

    rag_chain = {"context": retriever, 
             "question": question_feeder}|rag_prompt|chatbot

    answer = execute_chain(rag_chain, question)

    return answer