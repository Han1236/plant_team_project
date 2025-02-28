from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from operator import itemgetter
from utils.prompt_templates import qa_prompt
from utils.text_utils import translate_text

def create_stuff_documents_chain(llm):
    """LCEL을 사용하여 문서를 결합하는 체인을 생성합니다."""
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
        
    chain = (
        {
            "context": lambda x: format_docs(x["context"]),
            "chat_history": itemgetter("chat_history"),
            "input": itemgetter("input")
        }
        | qa_prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

def create_retrieval_chain(retriever, combine_docs_chain, memory_store):
    """LCEL을 사용하여 검색 기반 질의응답 체인을 생성합니다."""
    def split_query(input_dict):
        """쿼리를 번역하여 리트리버용과 메모리용으로 분리"""
        original_query = input_dict["input"]
        translated_query = translate_text(original_query)
        return {
            "retriever_query": translated_query,
            "memory_query": original_query,
            "chat_history": input_dict.get("chat_history", [])
        }

    base_chain = (
        RunnablePassthrough.assign(
            split_query=split_query
        )
        | {
            "context": lambda x: retriever.get_relevant_documents(x["split_query"]["retriever_query"]),
            "chat_history": lambda x: x["split_query"]["chat_history"],
            "input": lambda x: x["split_query"]["memory_query"]  # 원본 한글 쿼리 사용
        }
        | combine_docs_chain
    )
    
    # RunnableWithMessageHistory로 감싸기
    chain_with_memory = RunnableWithMessageHistory(
        base_chain,
        memory_store,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    
    return chain_with_memory
