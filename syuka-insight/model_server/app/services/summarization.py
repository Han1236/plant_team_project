from schemas.requests import SummarizeRequest
from utils.llm_utils import create_llm
from utils.prompt_templates import get_summarize_prompt
from langchain_core.output_parsers import StrOutputParser

def generate_summary(req: SummarizeRequest) -> str:
    """요약을 생성하는 함수"""
    try:
        model = create_llm(model_name="gemini-2.0-flash", temperature=0.7)
        
        # 요약 프롬프트 템플릿 얻기
        chatprompt = get_summarize_prompt(req.timeline, req.subtitle)
        
        # 체인 생성 및 실행
        chain = chatprompt | model | StrOutputParser()
        response = chain.invoke({})
        return response
    except Exception as e:
        print(f"Error in generate_summary: {str(e)}")
        raise e