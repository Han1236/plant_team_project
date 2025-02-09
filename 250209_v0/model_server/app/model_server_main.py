# model_server_main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv
import os
import traceback

# langchain 및 google generative ai 관련 모듈 임포트
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter

# rag_utils.py 임포트
from rag_utils import (
    create_db_from_transcript,
    embeddings_model,
    load_chroma_db,
    create_retriever_from_db,
    create_combine_docs_chain,
    create_retrieval_chain_from_db,
    qa_prompt,
    llm_qa,
    translate_text,
    memory
)

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError(
        "Google API Key가 설정되지 않았습니다. .env 파일에 GOOGLE_API_KEY=YOUR_API_KEY 를 설정해주세요."
    )

app = FastAPI(title="Model Server for Gemini + LangChain")

chromadb_list: List[Dict] = []

# ==== 데이터 모델 ====
class SummarizeRequest(BaseModel):
    text: str

class SummarizeResponse(BaseModel):
    summary: str

class ChatHistoryRequest(BaseModel):
    prompt: str
    video_id: str

class ChatHistoryResponse(BaseModel):
    answer: str


class CreateChromaDBRequest(BaseModel):
    video_id: str
    subtitle: str
    title: str

class CreateChromaDBResponse(BaseModel):
    success: bool
    message: str = ""

# ==== LangChain + Gemini 함수 ====
def gen_text(prompt: str) -> str:
    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp", temperature=0.7
    )
    chatprompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Youtube 영상 자막 내용입니다.
            이 내용을 보기 좋고 이해하기 쉽게 요약해주세요.
            주제를 제목으로 하여 가장 위에 배치하고,
            요약본은 전체적으로 마크다운 형식으로 작성해주세요.""",
            ),
            ("human", "{input}"),
        ]
    )
    chain = chatprompt | model
    response = chain.invoke({"input": prompt})
    return response.content


def get_rag_response(prompt: str, video_id: str) -> str:
    """RAG 기반 검색 질의응답 함수 (Non-streaming)."""
    global chroma_vector_store

    db_path = os.path.join("./chroma_db", video_id)
    collection_name = f"chroma_db_{video_id}"

    try:
        chroma_vector_store = load_chroma_db(db_path, collection_name, embeddings_model)
        if chroma_vector_store is None:
            return "ChromaDB 오류: DB 로드 실패"

        retriever = create_retriever_from_db(chroma_vector_store)
        combine_docs_chain = create_combine_docs_chain(llm_qa, qa_prompt)
        
        # retrieval_chain 생성 시 memory 추가
        retrieval_chain = (
            create_retrieval_chain_from_db(retriever, combine_docs_chain)
            | RunnablePassthrough.assign(
                chat_history=RunnableLambda(memory.load_memory_variables) | itemgetter("chat_history")
            )
        )

        translated_query = translate_text(prompt)
        print("번역된 질문:", translated_query)

        # memory에서 chat_history 가져오기
        current_history = memory.load_memory_variables({})["chat_history"]
        # print(f"Current history from memory: {current_history}") # current_history 확인


        # 스트리밍 대신 invoke 사용
        result = retrieval_chain.invoke(
            {"input": translated_query, "chat_history": current_history}, 
            config={"configurable": {"memory": memory}})
        # print(f"result: {result}") # result 확인

        memory.save_context({"input": prompt}, {"output": result["answer"]}) # 메모리에 저장
        # print(f"Memory after saving context: {memory.load_memory_variables({})}") # 메모리 확인

        return result['answer']  # 'answer' 키의 값 반환

    except Exception as e:
        print(f"Error in get_rag_response: {type(e).__name__} - {str(e)}")
        print(traceback.format_exc())
        return "RAG 처리 중 오류 발생"

# ==== FastAPI 라우터 ====

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
    """QnA 요청 처리 (Non-streaming)."""
    # print(f"Received request in model_server: {req.model_dump()}") # Received request 출력
    try:
        answer = get_rag_response(req.prompt, req.video_id)  # 응답 받기
        return ChatHistoryResponse(answer=answer)  # 응답 반환
    except Exception as e:
        print(f"Error in /chat endpoint: {type(e).__name__} - {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/chromadb_videos", response_model=List[Dict])
def get_chromadb_videos():
    return chromadb_list

@app.post("/create_chromadb", response_model=CreateChromaDBResponse)
def create_chromadb(req: CreateChromaDBRequest):
    try:
        success = create_db_from_transcript(
            req.subtitle, req.video_id, embeddings_model
        )
        if success:
            chromadb_list.append({"video_id": req.video_id, "title": req.title})
            return CreateChromaDBResponse(
                success=True, message=f"ChromaDB ({req.video_id}) 생성 성공!\n({req.title})"
            )
        else:
            return CreateChromaDBResponse(
                success=False, message=f"ChromaDB ({req.video_id}) 생성 실패.\n({req.title})"
            )
    except Exception as e:
        return CreateChromaDBResponse(
            success=False, message=f"ChromaDB 생성 중 오류 발생: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)