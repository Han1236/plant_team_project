from fastapi import APIRouter, HTTPException
from schemas.requests import SummarizeRequest
from schemas.responses import SummarizeResponse
from services.summarization import generate_summary

router = APIRouter()

@router.post("/summarize", response_model=SummarizeResponse)
def summarize(req: SummarizeRequest):
    try:
        summarized_text = generate_summary(req)
        return SummarizeResponse(summary=summarized_text)
    except Exception as e:
        print(f"Error in summarize: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summarize error: {str(e)}")