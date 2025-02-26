from typing import AsyncGenerator, List, Dict, Any
from utils.chroma_utils import load_chroma_db
from utils.text_utils import translate_text
# from utils.prompt_templates import qa_prompt
from utils.llm_utils import create_llm, get_embeddings_model
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
# from langchain.memory import ConversationBufferMemory
# from langchain_core.runnables import RunnablePassthrough, RunnableLambda
# from operator import itemgetter
import os
import traceback
import asyncio
from utils.chains import create_stuff_documents_chain, create_retrieval_chain
import logging
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser

# 로그 설정
logging.basicConfig(level=logging.DEBUG) # 로그 레벨 설정 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
logger = logging.getLogger(__name__) # 현재 모듈에 대한 로거 생성

# # 메모리 객체 생성
# memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# QA 모델
llm_qa = create_llm(model_name="gemini-2.0-flash", temperature=0.7, streaming=True)

async def get_rag_response_stream(query: str, video_id: str, chat_history: List = None) -> AsyncGenerator[str, None]:
    """RAG를 사용하여 응답을 생성하고 스트리밍합니다."""
    if chat_history is None:
        chat_history = []
        
    try:
        # chat_history를 BaseMessage 객체로 변환
        messages_history = []
        for msg in chat_history:
            if msg["role"] == "human":
                messages_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                messages_history.append(AIMessage(content=msg["content"]))
        
        logger.info(f"ChromaDB 로딩 중... (video_id: {video_id})")
        db_path = os.path.join("./chroma_db", video_id)
        collection_name = f"chroma_db_{video_id}"
        embeddings_model = get_embeddings_model()
        
        chroma_vector_store = load_chroma_db(db_path, collection_name, embeddings_model)
        if chroma_vector_store is None:
            yield "ChromaDB 오류: DB 로드 실패"
            return

        retriever = chroma_vector_store.as_retriever(kwargs={"k": 5})
        
        # LLM 초기화
        llm = create_llm(model_name="gemini-2.0-flash", temperature=0.7, streaming=True)
        
        # 체인 생성
        stuff_chain = create_stuff_documents_chain(llm)
        retrieval_chain = create_retrieval_chain(retriever, stuff_chain)

        translated_query = translate_text(query)
        logger.info(f"번역된 질문: {translated_query}")
        
        # 스트리밍 응답 처리
        full_response = ""
        try:
            async for chunk in retrieval_chain.astream({
                "input": translated_query,
                "chat_history": messages_history
            }):
                if chunk:
                    content = chunk
                    full_response += content
                    yield content

            # 대화 내용 저장
            chat_history.append({"role": "human", "content": query})
            chat_history.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            logger.error(f"스트리밍 처리 중 오류 발생: {str(e)}")
            logger.error(traceback.format_exc())
            yield "스트리밍 처리 중 오류가 발생했습니다."

    except Exception as e:
        logger.error(f"RAG 처리 중 오류 발생: {str(e)}")
        logger.error(traceback.format_exc())
        yield "RAG 처리 중 오류가 발생했습니다."