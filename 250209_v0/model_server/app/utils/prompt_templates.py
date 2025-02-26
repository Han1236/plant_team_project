from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# QnA 프롬프트 템플릿
qa_prompt = ChatPromptTemplate([
    ("system", "Please answer in Korean. Answer any user questions based solely on the context below, and consider the conversation history."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "<context>\n{context}\n</context>"),
    ("human", "{input}")
])

def get_summarize_prompt(timeline, subtitle):
    """요약 프롬프트 템플릿을 생성합니다."""
    system_prompt = f"""당신은 YouTube 영상의 자막과 타임라인을 분석하여 구조화된 요약을 제공하는 전문가입니다.
    
    다음 규칙을 따라 요약을 작성해주세요:
    1. 전체 영상의 주제를 대표하는 제목을 ## 형식으로 작성하세요.
    2. 전체 내용에 대한 간단한 소개를 작성하세요.
    3. 타임라인의 각 구간별로 다음 형식으로 요약하세요:
    ### 적절한 이모티콘, 수정한 제목
    - 핵심 내용 요약 (bullet points)
    - 구체적인 내용 설명(중요한 키워드에는 ** 표시해서 강조)
    - 구간 별 중간 요약으로 한줄 정리
    4. 마지막에 전체 내용의 핵심 포인트를 3줄로 정리해주세요.
    
    타임라인 정보:
    {timeline}
    
    자막 내용:
    {subtitle}
    """
    
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "위 내용을 요약해주세요.")
    ])