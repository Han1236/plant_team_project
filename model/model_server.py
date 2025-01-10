from fastapi import FastAPI, Request
from transformers import pipeline

app = FastAPI()

# 요약 모델 로드
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.post("/summarize")
async def summarize(request: Request):
    body = await request.json()
    text = body.get("text", "")
    summary = summarizer(text, max_length=130, min_length=30, do_sample=False)
    return {"summary": summary[0]["summary_text"]}

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = body.get("message", "")
    # 예제: 간단한 에코
    return {"response": f"You said: {message}"}

# from fastapi import FastAPI, HTTPException
# import requests



# app = FastAPI()

# # Gemini API 설정
# GEMINI_API_URL = "https://api.gemini.com/v1/some-endpoint"
# GEMINI_API_KEY = "your_gemini_api_key_here"

# def call_gemini_api(data):
#     headers = {
#         "Authorization": f"Bearer {GEMINI_API_KEY}",
#         "Content-Type": "application/json",
#     }
#     response = requests.post(GEMINI_API_URL, json=data, headers=headers)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         raise HTTPException(status_code=response.status_code, detail=response.text)

# @app.post("/process_data")
# async def process_data(input_data: dict):
#     try:
#         result = call_gemini_api(input_data)
#         return {"gemini_response": result}
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


