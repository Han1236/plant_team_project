from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableWithMessageHistory
from operator import itemgetter
from utils.prompt_templates import qa_prompt
from langchain_core.messages import HumanMessage, AIMessage
import logging

logger = logging.getLogger(__name__)

def create_stuff_documents_chain(llm):
    """LCEL을 사용하여 문서를 결합하는 체인을 생성합니다."""
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)
        
    chain = (
        {
            "context": lambda x: format_docs(x["context"]),
            "chat_history": itemgetter("chat_history"),  # 직접 chat_history 사용
            "input": itemgetter("input")
        }
        | qa_prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

def create_retrieval_chain(retriever, combine_docs_chain, memory_store):
    """LCEL을 사용하여 검색 기반 질의응답 체인을 생성합니다."""
    base_chain = (
        {
            "context": itemgetter("input") | retriever,
            "chat_history": itemgetter("chat_history"),
            "input": itemgetter("input")
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
