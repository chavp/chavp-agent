การติดตั้ง Jupyter Notebook ร่วมกับ CUDA บน Windows เพื่อใช้งาน GPU (เช่นการทำ Deep Learning) มีขั้นตอนสำคัญที่ต้องทำตามลำดับเพื่อให้ Library ต่างๆ มองเห็นการ์ดจอ ดังนี้ครับ

---

### 1. ตรวจสอบฮาร์ดแวร์และติดตั้ง Driver
ก่อนอื่นต้องแน่ใจว่าใช้การ์ดจอ **NVIDIA** และติดตั้ง Driver เวอร์ชันล่าสุด
* ไปที่ [NVIDIA Driver Downloads](https://www.nvidia.com/Download/index.aspx)
* เลือกซีรีส์การ์ดจอของคุณและติดตั้งให้เรียบร้อย

### 2. ติดตั้ง CUDA Toolkit
CUDA คือหัวใจสำคัญที่ทำให้ Python คุยกับ GPU ได้
* ไปที่ [CUDA Toolkit Archive](https://developer.nvidia.com/cuda-toolkit-archive)
* **ข้อแนะนำ:** แนะนำเวอร์ชัน **11.8** หรือ **12.x** (ตรวจสอบกับ Library ที่จะใช้ เช่น PyTorch หรือ TensorFlow ว่ารองรับเวอร์ชันไหน)
* เลือก Windows > x86_64 > 11 > exe (local) แล้วติดตั้งตามขั้นตอน

### 3. ติดตั้ง cuDNN (Optional แต่แนะนำ)
cuDNN เป็น Library เสริมที่ช่วยให้การคำนวณ Deep Learning เร็วขึ้น
* ดาวน์โหลดจาก [NVIDIA cuDNN](https://developer.nvidia.com/cudnn) (ต้องสมัครสมาชิก NVIDIA Developer)
* แตกไฟล์ zip แล้วก๊อปปี้ไฟล์ในโฟลเดอร์ `bin`, `include`, และ `lib` ไปวางทับในโฟลเดอร์ที่ติดตั้ง CUDA (ปกติอยู่ที่ `C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\vX.X`)

### 4. ติดตั้ง Anaconda หรือ Miniconda
เพื่อการจัดการสภาพแวดล้อม (Environment) ที่สะอาด แนะนำให้ใช้ Conda ครับ
1.  ดาวน์โหลดและติดตั้ง [Miniconda](https://docs.conda.io/en/latest/miniconda.html)
2.  เปิด **Anaconda Prompt** ขึ้นมาแล้วสร้าง Environment ใหม่:
    ```bash
    conda create -n gpu_env python=3.13.9
    conda activate gpu_env
    ```

### 5. ติดตั้ง Jupyter และ Deep Learning Library
ใน Environment ที่สร้างขึ้น ให้ติดตั้ง Jupyter และ Library ที่รองรับ CUDA (ตัวอย่างนี้คือ PyTorch):
```bash
# ติดตั้ง Jupyter
pip install notebook ipykernel

# ติดตั้ง PyTorch (ตรวจสอบ command ล่าสุดที่ pytorch.org)
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu126

# เชื่อม Environment เข้ากับ Jupyter
python -m ipykernel install --user --name=gpu_env --display-name "Python (GPU)"
```

### 6. ตรวจสอบการใช้งานใน Jupyter
1.  พิมพ์ `jupyter notebook` ใน Prompt
2.  สร้างไฟล์ใหม่ เลือก Kernel เป็น **"Python (GPU)"** ที่เราสร้างไว้
3.  รัน Code เพื่อเช็คว่ามองเห็น GPU หรือไม่:
    ```python
    import torch
    print(torch.cuda.is_available())
    print(torch.cuda.get_device_name(0))
    ```
    *ถ้าขึ้นว่า `True` แสดงว่าพร้อมใช้งานแล้วครับ*

---

**มีขั้นตอนไหนที่ติดขัดหรือต้องการให้ช่วยเลือกเวอร์ชัน CUDA ให้เหมาะกับการ์ดจอที่ใช้อยู่ไหมครับ?**