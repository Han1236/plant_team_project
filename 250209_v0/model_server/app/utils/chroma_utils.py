from langchain_chroma import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

# 텍스트 분할기
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# ChromaDB 기본 경로
DB_PATH = "./chroma_db"

def create_chroma_db_from_documents(docs, persist_directory, collection_name, embedding_model):
    """문서들로부터 ChromaDB를 생성합니다."""
    chroma_vector_store = Chroma.from_documents(
        documents=docs,
        embedding=embedding_model,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    return chroma_vector_store

def load_chroma_db(persist_directory, collection_name, embedding_model):
    """ChromaDB를 로드합니다."""
    if not os.path.exists(persist_directory):
        return None

    try:
        chroma_vector_store = Chroma(
            persist_directory=persist_directory,
            embedding_function=embedding_model,
            collection_name=collection_name
        )
        return chroma_vector_store
    except Exception as e:
        print(f"ChromaDB 로딩 에러: {e}")
        return None

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
    """DB에서 검색 Retriever를 생성합니다."""
    return chroma_vector_store.as_retriever(search_kwargs=search_kwargs)

def split_text_into_documents(text, text_splitter):
    """텍스트를 문서로 분할합니다."""
    texts = text_splitter.split_text(text)
    docs = text_splitter.create_documents(texts)
    return docs