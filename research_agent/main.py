from typing import Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel

from web_scraping import web_scrape
from web_searching import web_search
from chain_5_1 import web_research_chain

# 1. ใส่ข้อมูลภาพรวมของ API ในแอปพลิเคชัน
app = FastAPI(
    title="ระบบจัดการคลังสินค้า (Warehouse API)",
    description="API สำหรับจัดการสินค้าคงคลัง ตรวจสอบสต็อก และอัปเดตสถานะการจัดส่ง",
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "ทีมพัฒนาซอฟต์แวร์",
        "url": "http://example.com/contact",
        "email": "support@example.com",
    },
)

# 2. ปรับแต่งข้อมูลของ Model (Request/Response Body)
class Item(BaseModel):
    name: str = "โน้ตบุ๊กไร้สาย" # กำหนด Default/Example Value
    price: float
    description: Optional[str] = None

    class Config:
        # ใส่ตัวอย่างข้อมูลที่จะไปโชว์บนหน้า Docs
        schema_extra = {
            "example": {
                "name": "Gaming Laptop",
                "price": 35900.00,
                "description": "โน้ตบุ๊กสำหรับเล่นเกมสเปกสูง"
            }
        }

# 2. สร้าง Route หรือ Endpoint
@app.get("/")
def read_root():
    return {"message": "ยินดีต้อนรับสู่ FastAPI!"}

@app.get("/items")
def read_items():
    return {"item_id": item_id, "query": q}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}

# 3. ใส่แท็ก (Tags) และคำอธิบายในส่วนของ Endpoint
@app.post("/items/", tags=["จัดการสินค้า"], summary="สร้างสินค้าชิ้นใหม่")
def create_item(item: Item):
    """
    สร้างสินค้าใหม่ในระบบพร้อมรายละเอียดราคาและคำอธิบาย:
    - **name**: ชื่อสินค้า (จำเป็นต้องใส่)
    - **price**: ราคาสินค้า
    """
    return {"message": "เพิ่มสินค้าเรียบร้อย", "data": item}

@app.get("/run-info-cuda", tags=["system"], summary="แสดงข้อมูล run GPU")
def get_run_info_cuda():
    import torch
    # 1. ตรวจสอบว่าระบบรองรับ CUDA หรือไม่ (True/False)
    cuda_available = torch.cuda.is_available()

    if cuda_available:
        # 2. นับจำนวน GPU ที่มีในเครื่อง
        device_count = torch.cuda.device_count()

        # 3. ดูชื่อรุ่นของ GPU ตัวหลัก (ID: 0)
        current_device = torch.cuda.current_device()
        gpu_name = torch.cuda.get_device_name(current_device)

        # 4. ดูสเปก Compute Capability ของ GPU
        capability = torch.cuda.get_device_capability(current_device)

        return {
            "cuda_available": cuda_available,
            "device_count": f"GPU Count: {device_count}",
            "current_device": f"Current GPU Device: ID {current_device} -> {gpu_name}",
            "capability": f"CUDA Capability: {capability[0]}.{capability[1]}"
        }
    else:
        return {
            "cuda_available": cuda_available,
            "torch.cuda.is_available": "PyTorch detect เฉพาะ CPU (ไม่พบ CUDA GPU หรือยังไม่ได้ติดตั้ง PyTorch เวอร์ชัน CUDA"
        }

@app.get("/web-scrape", tags=["research_agents"], summary="WEB Scrapping", description="https://en.wikipedia.org/wiki/List_of_career_achievements_by_Michael_Jordan")
def get_web_scrape(url: str = Query(..., description="URL ของเว็บไซต์ที่ต้องการให้ดึงข้อมูล")):
    result = web_scrape(url)
    return result

@app.get("/web-search", tags=["research_agents"], summary="WEB search", description="How many titles did Michael Jordan win?")
def get_web_search(query: str = Query(..., description="ข้อมูลดึงเว็บไซต์ที่ต้องการ")):
    result = web_search(query, num_results=5)
    return result

@app.get("/chain-try-5-1", tags=["research_agents"], summary="chain_try_5_1", description="What can I see and do in the Spanish town of Astorga?")
def get_chain_try_5_1(question: str = Query(..., description="test chain invocation")):
    web_research_report = web_research_chain.invoke(question)
    return web_research_report