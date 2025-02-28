from fastapi import APIRouter, HTTPException
import requests
import os
from schemas.requests import ChromaDBRequest
from typing import List, Dict, Any

router = APIRouter(tags=["ChromaDB"])

MODEL_SERVER_URL = os.getenv("MODEL_SERVER_URL", "http://model-server:8001")

@router.post("/create_chromadb")
def create_chromadb(request: ChromaDBRequest):
    """ChromaDB에 자막 데이터를 저장합니다."""
    try:
        payload = {
            "video_id": request.video_id, 
            "title": request.title, 
            "subtitle": request.subtitle
        }
        response = requests.post(f"{MODEL_SERVER_URL}/create_chromadb", json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.get("/chromadb_videos", response_model=List[Dict])
def get_chromadb_videos():
    """저장된 ChromaDB 비디오 목록을 가져옵니다."""
    try:
        response = requests.get(f"{MODEL_SERVER_URL}/chromadb_videos")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"ChromaDB 목록 가져오기 실패: {str(e)}")