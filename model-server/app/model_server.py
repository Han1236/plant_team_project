from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv
import os

# langchain & google generative ai
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.memory import ChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

# .env 로드 (GOOGLE_API_KEY 등)
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("Google API Key가 설정되지 않았습니다.")

# ==== FastAPI 초기화 ====
app = FastAPI(title="Model Server for Gemini + LangChain")

# ==== 데이터 모델 ====
class SummarizeRequest(BaseModel):
    text: str

class SummarizeResponse(BaseModel):
    summary: str

class ChatHistoryRequest(BaseModel):
    prompt: str
    history: List[Dict[str, str]] = []  # role: "user"/"assistant", content: "..."

class ChatHistoryResponse(BaseModel):
    response: str

# ==== LangChain + Gemini 함수 ====
def gen_text(prompt: str) -> str:
    """
    자막 또는 긴 텍스트를 요약하기 위한 chain.
    """
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.7,
        # key=GOOGLE_API_KEY 등 (라이브러리에서 기본적으로 .env 불러오는 경우도 있음)
    )
    # system / human 메시지 정의
    chatprompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Youtube 영상 자막 내용입니다.  
                이 내용을 보기 좋고 이해하기 쉽게 요약해주세요.  
                주제를 제목으로 하여 가장 위에 배치하고,  
                요약본은 전체적으로 마크다운 형식으로 작성해주세요."""
            ),
            ("human", "{input}"),
        ]
    )
    chain = chatprompt | model
    response = chain.invoke({"input": prompt})
    return response.content

def gen_chat(prompt: str, history: ChatMessageHistory) -> str:
    """
    사용자의 질문(prompt)과 기존 챗 히스토리를 바탕으로 응답.
    """
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=0.7,
    )
    chatprompt = ChatPromptTemplate.from_messages(
        [
            ("system", "너는 Youtube 영상 자막을 바탕으로 QnA하는 챗봇이야."),
            ("human", "{input}"),
        ]
    )
    chain = chatprompt | model

    # langchain의 ChatMessageHistory -> messages
    messages = []
    for msg in history.messages:
        if isinstance(msg, SystemMessage):
            messages.append({"role": "system", "content": msg.content})
        elif isinstance(msg, HumanMessage):
            messages.append({"role": "human", "content": msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role": "assistant", "content": msg.content})

    # 실제 chain.invoke() 시, history를 어떻게 반영할지는
    # custom prompt / conversation buffer 등을 활용.
    # 여기서는 단순히 현재 prompt에만 넣는 예시:
    response = chain.invoke({"input": prompt, "history": messages})
    return response.content

# ==== 라우터 ====
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "model_server is running"}

@app.post("/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest):
    try:
        summarized_text = gen_text(req.text)
        return SummarizeResponse(summary=summarized_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarize error: {str(e)}")

@app.post("/chat", response_model=ChatHistoryResponse)
def chat(req: ChatHistoryRequest):
    """
    이전 대화 히스토리 + 현재 사용자 질문(req.prompt)을 종합하여 답변
    history = [
      {"role": "user", "content": "..."},
      {"role": "assistant", "content": "..."},
      ...
    ]
    """
    try:
        # langchain의 ChatMessageHistory에 적재
        chat_history = ChatMessageHistory()
        for msg in req.history:
            if msg["role"] == "user":
                chat_history.add_user_message(msg["content"])
            elif msg["role"] == "assistant":
                chat_history.add_ai_message(msg["content"])

        result = gen_chat(req.prompt, chat_history)
        return ChatHistoryResponse(response=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
