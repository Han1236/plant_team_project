from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.memory import ConversationBufferMemory
import os

# 메모리 객체 생성
memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True
)

# --- 모델 및 프롬프트 설정 ---
llm_translate = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
translate_prompt = ChatPromptTemplate(
    [
        ("system", "Only translate"),  # 시스템 프롬프트: '번역만 수행'
        ("human", """Translate: {input}

Answer: Only translate in English.""")  
    ]
)

# QnA를 위한 모델 및 프롬프트 설정
qa_prompt = ChatPromptTemplate(
    [
        ("system", "Please answer in Korean. Answer any user questions based solely on the context below, and consider the conversation history."),  # 시스템 프롬프트: 답변은 한국어로
        MessagesPlaceholder(variable_name="chat_history"),  # 대화 기록 위치
        ("human", "<context>\n{context}\n</context>"),  # 질문에 대한 문맥
        ("human", "{input}")  # 실제 사용자가 입력한 질문
    ]
)

# QnA 모델 설정 (스트리밍을 지원하는 모델)
llm_qa = ChatGoogleGenerativeAI(model="gemini-2.0-flash", streaming=True)

# 임베딩 모델 설정
embeddings_model = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

# 텍스트 분할기 설정 (문서가 너무 클 경우 잘라서 처리)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)


# --- ChromaDB 관련 변수 ---
DB_PATH = "./chroma_db"  # Chroma DB 저장 경로
COLLECTION_NAME = "chroma_db"  # Collection 이름 설정
chroma_vector_store = None  # Chroma DB 상태를 전역 변수로 관리

# --- ChromaDB 관련 함수 ---
def create_chroma_db_from_documents(docs, persist_directory, collection_name, embedding_model):
    """주어진 문서들을 ChromaDB로 변환하여 저장하는 함수."""
    chroma_vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    return chroma_vector_store

def load_chroma_db(persist_directory, collection_name, embedding_model):
    """저장된 Chroma DB를 로드하는 함수."""
    if not os.path.exists(persist_directory):  # DB 경로가 없다면 None 반환
        return None

    try:
        # Chroma DB를 로드
        chroma_vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model,
            collection_name=collection_name
        )
        return chroma_vector_store
    except Exception as e:  # 로딩 중 에러 발생 시 None 반환
        print(f"ChromaDB 로딩 에러: {e}") # 에러 로그 출력
        return None

# --- ChromaDB 생성 함수 ---
def create_db_from_transcript(subtitle, video_id, embedding_model):
    """영상의 자막을 사용해 ChromaDB를 생성하는 함수."""
    global chroma_vector_store

    # DB 경로 및 Collection 이름 동적 생성 (video_id 기반)
    db_path = os.path.join(DB_PATH, video_id)  # 예시: ./chroma_db/videoId123 
    collection_name = f"chroma_db_{video_id}"  # 예시: chroma_db_videoId123

    # DB 경로 확인: 이미 존재하면 중복 생성 방지
    if os.path.exists(db_path):
        print(f"ChromaDB already exists at {db_path}. Skipping creation.")
        raise FileExistsError(f"이미 ChromaDB 존재합니다.")


    if subtitle:  # 자막이 있으면 Chroma DB 생성
        docs = split_text_into_documents(subtitle, text_splitter)  # 자막을 문서로 분할

        # Chroma DB 생성
        try:
            chroma_vector_store = create_chroma_db_from_documents(
                docs, db_path, collection_name, embedding_model  # 동적 경로 및 이름 사용
            )
            return True  # DB 생성 성공 시 True 반환
        except Exception as e:
            print(f"ChromaDB 생성 에러: {e}") # 에러 로그 출력
            return False # DB 생성 실패 시 False 반환
    else:  # 자막이 없으면 실패 처리
        print("자막이 없어 ChromaDB를 생성할 수 없습니다.") # 로그 출력
        return False # DB 생성 실패 시 False 반환


def create_retriever_from_db(chroma_vector_store, search_kwargs={'k': 5}):
    """Chroma DB에서 검색 기능을 담당하는 Retriever 생성 함수."""
    retriever = chroma_vector_store.as_retriever(search_kwargs=search_kwargs)
    return retriever

def create_combine_docs_chain(llm, prompt):
    """문서를 결합하는 Langchain 체인 생성 함수."""
    return create_stuff_documents_chain(llm, prompt)

def create_retrieval_chain_from_db(retriever, combine_docs_chain):
    """검색 기반 질의응답 체인 생성 함수."""
    return create_retrieval_chain(retriever, combine_docs_chain)

def split_text_into_documents(text, text_splitter):
    """긴 텍스트를 여러 문서로 분할하는 함수."""
    texts = text_splitter.split_text(text)  # 텍스트를 일정 크기로 분할
    docs = text_splitter.create_documents(texts)  # Langchain 문서 객체로 변환
    return docs

def translate_text(input_text):
    """주어진 텍스트를 번역하는 함수."""
    chain = translate_prompt | llm_translate  # 번역 프롬프트와 모델 연결
    result = chain.invoke({"input": input_text})  # 번역 실행
    return result.content