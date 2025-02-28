from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
import os

# 환경 변수 로드
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def create_llm(model_name="gemini-2.0-flash", temperature=0.7, streaming=False):
    """LLM 모델을 생성합니다."""
    return ChatGoogleGenerativeAI(
        model=model_name, 
        temperature=temperature,
        streaming=streaming
    )

def get_embeddings_model():
    """임베딩 모델을 반환합니다."""
    return GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")