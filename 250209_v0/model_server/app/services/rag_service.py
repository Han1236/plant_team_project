from typing import AsyncGenerator
from utils.chroma_utils import load_chroma_db, create_retriever_from_db
from utils.text_utils import translate_text
from utils.prompt_templates import qa_prompt
from utils.llm_utils import create_llm, get_embeddings_model
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from operator import itemgetter
import os
import traceback

# 메모리 객체 생성
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# QA 모델
llm_qa = create_llm(model_name="gemini-2.0-flash", temperature=0.7, streaming=True)

def create_combine_docs_chain(llm, prompt):
    """문서를 결합하는 Langchain 체인 생성 함수."""
    return create_stuff_documents_chain(llm, prompt)

def create_retrieval_chain_from_db(retriever, combine_docs_chain):
    """검색 기반 질의응답 체인 생성 함수."""
    return create_retrieval_chain(retriever, combine_docs_chain)

async def get_rag_response_stream(prompt: str, video_id: str) -> AsyncGenerator[str, None]:
    """RAG 기반 검색 질의응답 함수 (Streaming)."""
    db_path = os.path.join("./chroma_db", video_id)
    collection_name = f"chroma_db_{video_id}"
    embeddings_model = get_embeddings_model()

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