@echo off
REM Activate Anaconda environment and run FastAPI
call D:\Users\asus\anaconda3\Scripts\conda.bat activate gpu_env
D:\Users\asus\anaconda3\envs\gpu_env\Scripts\pip.exe install -r requirements.txt
D:\Users\asus\anaconda3\envs\gpu_env\Scripts\uvicorn.exe main:app --reload --host 127.0.0.1 --port 8000
pause
