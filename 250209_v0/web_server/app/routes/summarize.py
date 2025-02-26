from fastapi import APIRouter, HTTPException
from schemas.requests import TextRequest
from services.model_service import summarize_text
import json

router = APIRouter(tags=["Summarize"])

@router.post("/summarize")
def summarize(request: TextRequest):
    """텍스트 요약을 처리합니다."""
    try:
        # 타임라인과 자막 정보를 분리
        data = json.loads(request.prompt)
        timeline = data.get("timeline", "타임라인 정보가 없습니다.")
        subtitle = data.get("subtitle", "")

        # 모델 서버에 요약 요청
        return summarize_text(timeline, subtitle)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))