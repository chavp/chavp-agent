from fastapi import FastAPI, Query
from dotenv import load_dotenv
import os
import chromadb
chroma_client = chromadb.Client()
tourism_collection = chroma_client.create_collection(
    name="tourism_collection")
tourism_collection.add(
    documents=[
        "เพสตุม (Paestum) หรือ โพไซโดเนีย (Poseidonia) ในภาษากรีก คือเมืองโบราณทางตอนใต้ของอิตาลี ใกล้กับชายฝั่งตะวันตก ตั้งอยู่ทางทิศตะวันออกเฉียงใต้ของเมืองซาเลร์โน (Salerno) ในปัจจุบันประมาณ 22 ไมล์ (35 กิโลเมตร) และอยู่ทางทิศใต้ของแม่น้ำเซเล (Sele) หรือแม่น้ำสิลารุส (Silarus) โบราณ ประมาณ 5 ไมล์ (8 กิโลเมตร) เมืองเพสตุมเป็นที่รู้จักกันดีจากวิหารกรีกที่ได้รับการอนุรักษ์ไว้อย่างงดงามตระการตา", 
        "โพไซโดเนียน่าจะถูกสร้างขึ้นเมื่อประมาณ 600 ปีก่อนคริสตกาล โดยชาวกรีกที่อพยพมาจากเมืองไซบาริส (Sybaris) บริเวณอ่าวตารันโต (Gulf of Taranto) และเมื่อพิจารณาจากวิหารต่าง ๆ แล้ว เมืองนี้ได้กลายเป็นเมืองที่เจริญรุ่งเรืองอย่างมากภายในปี 540 ก่อนคริสตกาล หลังจากต่อต้านอยู่นานหลายปี ในที่สุดเมืองนี้ก็ตกอยู่ภายใต้การปกครองของชาวลูคาเนีย (Lucanians) ซึ่งเป็นชนพื้นเมืองอิตาลิกในช่วงเวลาก่อน 400 ปีก่อนคริสตกาล และหลังจากนั้นเมืองก็ถูกเปลี่ยนชื่อเป็นเพสตุม ต่อมาพระเจ้าอเล็กซานเดอร์แห่งเอปิรัส (Alexander, king of Epirus) ได้ทรงรบชนะชาวลูคาเนียที่เมืองเพสตุมเมื่อประมาณ 332 ปีก่อนคริสตกาล ทว่าเมืองนี้ก็ยังคงเป็นของชาวลูคาเนียจนกระทั่งปี 273 ก่อนคริสตกาล เมื่อเมืองนี้ตกอยู่ใต้การปกครองของโรมันและมีการตั้งอาณานิคมละตินขึ้นที่นั่น เมืองนี้ได้ให้การสนับสนุนกรุงโรมในช่วงสงครามพูนิคครั้งที่สอง พื้นที่แถบนี้ยังคงมีความมั่งคั่งในช่วงปีแรก ๆ ของจักรวรรดิโรมัน แต่การสะสมของตะกอนดินที่ค่อย ๆ ปิดปากแม่น้ำสิลารุสในที่สุดก็ทำให้เกิดหนองน้ำที่เป็นแหล่งเพาะพันธุ์ไข้มาลาเรีย และเมืองเพสตุมก็ถูกทิ้งร้างไปอย่างสิ้นเชิงหลังจากถูกกลุ่มโจรสลัดมุสลิมเข้าปล้นสะดมในปี ค.ศ. 871 ซากปรักหักพังของพื้นที่ที่ถูกทิ้งร้างแห่งนี้ได้รับการค้นพบอีกครั้งในคริสต์ศตวรรษที่ 18",
        "พื้นที่ส่วนที่เป็นกรีกโบราณของเพสตุมประกอบด้วยเขตศักดิ์สิทธิ์สองแห่ง ซึ่งเป็นที่ตั้งของวิหารดอริก (Doric temples) สามแห่งที่อยู่ในสภาพที่ได้รับการอนุรักษ์ไว้อย่างน่าทึ่ง ในช่วงยุคโรมันต่อมา รูปแบบผังเมืองและฟอรัม (ลานกิจกรรมส่วนกลาง) ตามแบบฉบับโรมันได้ขยายตัวขึ้นระหว่างเขตศักดิ์สิทธิ์กรีกโบราณทั้งสองแห่งนี้ ในบรรดาวิหารทั้งสามแห่ง วิหารแห่งอาธีนา (หรือที่เรียกกันว่าวิหารแห่งเซเรส) และวิหารแห่งเฮราที่ 1 (หรือที่เรียกกันว่าบาซิลิกา) สร้างขึ้นตั้งแต่ศตวรรษที่ 6 ก่อนคริสตกาล ในขณะที่วิหารแห่งเฮราที่ 2 (หรือที่เรียกกันว่าวิหารแห่งเนปจูน) น่าจะสร้างขึ้นเมื่อประมาณ 460 ปีก่อนคริสตกาล และเป็นวิหารที่ได้รับการอนุรักษ์ไว้ดีที่สุดในบรรดาทั้งสามแห่ง ส่วนวิหารแห่งสันติภาพ (Temple of Peace) ในบริเวณฟอรัมนั้นเป็นอาคารสถาปัตยกรรมแบบคอรินเทียน-ดอริก ซึ่งอาจเริ่มสร้างในศตวรรษที่ 2 ก่อนคริสตกาล นอกจากนี้ยังมีการค้นพบร่องรอยของอัฒจันทร์โรมันและอาคารอื่น ๆ รวมถึงถนนสายหลักที่ตัดกันด้วย กำแพงเมืองโดยรอบซึ่งสร้างขึ้นจากบล็อกหินทราเวอร์ทีน (Travertine) มีความหนาประมาณ 15–20 ฟุต (5–6 เมตร) และมีความยาวโดยรอบประมาณ 3 ไมล์ (5 กิโลเมตร) ต่อมาในเดือนกรกฎาคม ค.ศ. 1969 ชาวนาคนหนึ่งได้ขุดพบสุสานลูคาเนียโบราณ ซึ่งภายในมีภาพจิตรกรรมฝาผนังแบบกรีก (Greek frescoes) ที่วาดในรูปแบบคลาสสิกตอนต้น (Early Classical style) พิพิธภัณฑ์โบราณคดีของเพสตุมได้เก็บรักษาโบราณวัตถุเหล่านี้และสมบัติล้ำค่าอื่น ๆ จากพื้นที่แห่งนี้เอาไว้"
    ],
    metadatas=[
        {"source": "https://www.britannica.com/place/Paestum"}, 
        {"source": "https://www.britannica.com/place/Paestum"},
        {"source": "https://www.britannica.com/place/Paestum"}
    ],
    ids=["paestum-br-01", "paestum-br-02", "paestum-br-03"]
)

from openai import OpenAI

load_dotenv() #A
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") #B
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def query_vector_database(question):
    results = tourism_collection.query(
    query_texts=[question],
    n_results=1)

    results_text = results['documents'][0][0]

    return results_text

def prompt_template(question, text):
    return f'Read the following text and answer this question: {question}. \nText: {text}'

def execute_llm_prompt(prompt_input):
    prompt_response = openai_client.chat.completions.create(
        model='gpt-5-nano',
        messages=[
         {"role": "system", "content": "You are an assistant for question-answering tasks."},
         {"role": "user", "content": prompt_input}
        ])
    return prompt_response

def my_chatbot(question):
    results_text = query_vector_database(question) #A    
    prompt_input = prompt_template(question, 
                                   results_text) #B
    prompt_output = execute_llm_prompt(
        prompt_input) #C

    return prompt_output

app = FastAPI(
    title="สร้างงานวิจัยด้วย LangGraph และ ChatGPT",
    description="API ค้นคว้างานวิจัย",
    version="1.0.0",
    terms_of_service="https://chavp.wordpress.com/about/",
    contact={
        "name": "ทีมพัฒนาซอฟต์แวร์",
        "url": "https://chavp.wordpress.com",
        "email": "my.parinya@gmail.com",
    },
)



@app.get("/tourism-chat", tags=["tourism_agent"], summary="ใส่คำถามข้อมูลท่องเที่ยว", description="Let me know how many temples there are in Paestum, who constructed them, and what  architectural style they are")
def get_tourism_chat(question: str = Query(..., description="question tourism")):
    result = my_chatbot(question)
    return result