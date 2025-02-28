from utils.llm_utils import create_llm
from langchain_core.prompts import ChatPromptTemplate

# 번역 모델
llm_translate = create_llm(model_name="gemini-2.0-flash")

# 번역 프롬프트
translate_prompt = ChatPromptTemplate([
    ("system", "Only translate"),
    ("human", """Translate: {input}

Answer: Only translate in English.""")
])

def translate_text(input_text):
    """텍스트를 영어로 번역합니다."""
    chain = translate_prompt | llm_translate
    result = chain.invoke({"input": input_text})
    return result.content