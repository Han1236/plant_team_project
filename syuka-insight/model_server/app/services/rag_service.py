from typing import AsyncGenerator, Dict
from utils.chroma_utils import load_chroma_db
from utils.llm_utils import create_llm, get_embeddings_model
from utils.chains import create_stuff_documents_chain, create_retrieval_chain
from langchain.memory import ChatMessageHistory
import os
import traceback
import logging
import json

# 로그 설정
logging.basicConfig(level=logging.DEBUG) # 로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logger = logging.getLogger(__name__) # 현재 모듈에 대한 로거 생성

# 전역 변수로 video_id별 메모리 저장
message_histories: Dict[str, ChatMessageHistory] = {}

# QA 모델
llm_qa = create_llm(model_name="gemini-2.0-flash", temperature=0.7, streaming=True)

def get_message_history(video_id: str):
    """video_id에 해당하는 메시지 히스토리를 가져옵니다."""
    if video_id not in message_histories:
        message_histories[video_id] = ChatMessageHistory()
    return message_histories[video_id]

async def get_rag_response_stream(query: str, video_id: str) -> AsyncGenerator[str, None]:
    """RAG를 사용하여 응답을 생성하고 스트리밍합니다."""
    try:
        logger.info(f"ChromaDB 로딩 중... (video_id: {video_id})")
        db_path = os.path.join("./chroma_db", video_id)
        collection_name = f"chroma_db_{video_id}"
        embeddings_model = get_embeddings_model()
        
        chroma_vector_store = load_chroma_db(db_path, collection_name, embeddings_model)
        if chroma_vector_store is None:
            yield json.dumps({"content": "ChromaDB 오류: DB 로드 실패"})
            return

        retriever = chroma_vector_store.as_retriever(kwargs={"k": 5})
        
        # 체인 생성
        stuff_chain = create_stuff_documents_chain(llm_qa)
        retrieval_chain = create_retrieval_chain(
            retriever, 
            stuff_chain,
            get_message_history
        )

        try:
            logger.info("스트리밍 응답 시작")
            
            # config에 session_id 추가
            config = {"configurable": {"session_id": video_id}}

            async for chunk in retrieval_chain.astream(
                {"input": query},  # 번역하지 않은 원본 쿼리 사용
                config=config
            ):
                if chunk:
                    logger.info(f"전송할 content: {chunk}")
                    yield json.dumps({"content": chunk})

        except Exception as e:
            logger.error(f"스트리밍 처리 중 오류 발생: {str(e)}")
            logger.error(traceback.format_exc())
            yield json.dumps({"content": "스트리밍 처리 중 오류가 발생했습니다."})

    except Exception as e:
        logger.error(f"RAG 처리 중 오류 발생: {str(e)}")
        logger.error(traceback.format_exc())
        yield json.dumps({"content": "RAG 처리 중 오류가 발생했습니다."})