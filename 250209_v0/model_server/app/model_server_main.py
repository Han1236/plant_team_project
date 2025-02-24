# model_server_main.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, AsyncGenerator
from dotenv import load_dotenv
import os
import traceback
import asyncio
import json

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


async def get_rag_response_stream(prompt: str, video_id: str) -> AsyncGenerator[str, None]:
    """RAG 기반 검색 질의응답 함수 (Streaming)."""
    global chroma_vector_store

    db_path = os.path.join("./chroma_db", video_id)
    collection_name = f"chroma_db_{video_id}"

    try:
        chroma_vector_store = load_chroma_db(db_path, collection_name, embeddings_model)
        if chroma_vector_store is None:
            yield "ChromaDB 오류: DB 로드 실패"
            return

        retriever = create_retriever_from_db(chroma_vector_store)
        combine_docs_chain = create_combine_docs_chain(llm_qa, qa_prompt)
        
        retrieval_chain = (
            create_retrieval_chain_from_db(retriever, combine_docs_chain)
            | RunnablePassthrough.assign(
                chat_history=RunnableLambda(memory.load_memory_variables) | itemgetter("chat_history")
            )
        )

        translated_query = translate_text(prompt)
        current_history = memory.load_memory_variables({})["chat_history"]

        # 스트리밍 응답 처리
        async for chunk in retrieval_chain.astream(
            {"input": translated_query, "chat_history": current_history},
            config={"configurable": {"memory": memory}}
        ):
            if "answer" in chunk:
                yield chunk["answer"]

        # 대화 내용 메모리에 저장
        final_response = "".join([chunk["answer"] async for chunk in retrieval_chain.astream(
            {"input": translated_query, "chat_history": current_history}
        )])
        memory.save_context({"input": prompt}, {"output": final_response})

    except Exception as e:
        print(f"Error in get_rag_response_stream: {type(e).__name__} - {str(e)}")
        print(traceback.format_exc())
        yield "RAG 스트리밍 처리 중 오류 발생"

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

@app.post("/chat/stream")
async def chat_stream(req: ChatHistoryRequest):
    """QnA 스트리밍 요청 처리."""
    try:
        # ChromaDB 로드
        db_path = os.path.join("./chroma_db", req.video_id)
        collection_name = f"chroma_db_{req.video_id}"
        
        chroma_vector_store = load_chroma_db(db_path, collection_name, embeddings_model)
        if chroma_vector_store is None:
            raise HTTPException(status_code=500, detail="ChromaDB 로드 실패")

        async def generate():
            try:
                retriever = create_retriever_from_db(chroma_vector_store)
                combine_docs_chain = create_combine_docs_chain(llm_qa, qa_prompt)
                
                translated_query = translate_text(req.prompt)
                current_history = memory.load_memory_variables({})["chat_history"]
                
                # 문서 검색
                docs = await retriever.aget_relevant_documents(translated_query)
                
                # 전체 응답을 저장할 변수
                full_response = ""
                
                # 응답 생성 및 스트리밍
                async for chunk in combine_docs_chain.astream({
                    "input": translated_query,
                    "chat_history": current_history,
                    "context": docs
                }):
                    if chunk:
                        # 청크 처리
                        chunk_text = ""
                        if isinstance(chunk, dict) and "answer" in chunk:
                            chunk_text = chunk["answer"]
                        elif isinstance(chunk, str):
                            chunk_text = chunk
                            
                        if chunk_text:
                            full_response += chunk_text
                            yield f"data: {chunk_text}\n\n"
                
                # 스트림 종료 신호
                yield "data: [DONE]\n\n"
                
                # 메모리에 대화 저장
                memory.save_context(
                    {"input": req.prompt},
                    {"output": full_response}
                )

            except Exception as e:
                print(f"Error in generate: {str(e)}")
                print(f"Error details: {traceback.format_exc()}")
                yield f"data: Error: {str(e)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        print(f"Error in chat_stream: {str(e)}")
        print(f"Error details: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

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