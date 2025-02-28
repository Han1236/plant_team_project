from fastapi import APIRouter
from schemas.requests import CreateChromaDBRequest
from schemas.responses import CreateChromaDBResponse
from services.db_service import create_chromadb, get_chromadb_list

router = APIRouter()

@router.get("/chromadb_videos")
def get_chromadb_videos():
    return get_chromadb_list()

@router.post("/create_chromadb", response_model=CreateChromaDBResponse)
def create_chromadb_endpoint(req: CreateChromaDBRequest):
    return create_chromadb(req)