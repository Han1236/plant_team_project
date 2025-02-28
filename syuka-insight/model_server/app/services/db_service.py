from typing import List, Dict
from schemas.requests import CreateChromaDBRequest
from schemas.responses import CreateChromaDBResponse
from utils.chroma_utils import create_db_from_transcript
from utils.llm_utils import get_embeddings_model

# ChromaDB 비디오 목록
chromadb_list: List[Dict] = []

def get_chromadb_list() -> List[Dict]:
    """ChromaDB 비디오 목록을 반환합니다."""
    return chromadb_list

def create_chromadb(req: CreateChromaDBRequest) -> CreateChromaDBResponse:
    """ChromaDB를 생성합니다."""
    try:
        embeddings_model = get_embeddings_model()
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