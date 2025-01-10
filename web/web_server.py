from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import httpx

app = FastAPI()

MODEL_SERVER_URL = "http://model-server:8001"

@app.post("/summarize_file")
async def summarize_file(file: UploadFile = File(...)):
    # 파일 읽기
    @app.post("/summarize_file")
    async def summarize_file(file: UploadFile = File(...)):
        if not file:
            return JSONResponse(content={"error": "파일이 업로드되지 않았습니다."}, status_code=400)

        # 파일 읽기
        try:
            content = await file.read()
            # 실제 요약 처리 로직 추가
            summary = "요약된 텍스트 예제"
            return JSONResponse(content={"summary": summary})
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)
    # content = await file.read()
    # text = content.decode("utf-8")
    
    # 파일 처리 및 요약
    summary = "요약"
    return JSONResponse(content={"summary":summary})
    
    # 모델 서버로 전달
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MODEL_SERVER_URL}/summarize", json={"text": text})
        return response.json()

@app.post("/chat")
async def chat(message: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{MODEL_SERVER_URL}/chat", json={"message": message})
        return response.json()


    