from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# QnA 프롬프트 템플릿
# qa_prompt = ChatPromptTemplate([
#     ("system", "Please answer in Korean. Answer any user questions based solely on the context below, and consider the conversation history."),
#     MessagesPlaceholder(variable_name="chat_history"),
#     ("human", "<context>\n{context}\n</context>"),
#     ("human", "{input}")
# ])

qa_prompt = ChatPromptTemplate([
    # 시스템 역할 정의
    ("system", """당신은 YouTube 영상의 내용을 분석하여 질문에 대한 답변을 제공하는 AI입니다. 
    다음 규칙을 철저히 따르세요:
    
    1. 답변은 반드시 한국어로 작성하세요.
    2. 질문에 대한 답변은 아래 제공된 컨텍스트(영상 정보)만을 기반으로 하세요.
    3. 사용자가 질문을 이해하기 쉽도록 중요 키워드는 강조(**) 표시하세요.
    4. 너무 짧거나 단답형으로 답하지 말고, 충분한 정보를 포함하여 자연스럽게 설명하세요.
    5. 불확실한 내용이 있다면 추측하지 말고 '해당 정보는 영상에 없습니다'라고 답변하세요.
    """),

    # 대화 히스토리 (과거 대화 내용 고려)
    MessagesPlaceholder(variable_name="chat_history"),

    # 컨텍스트 정보 제공
    ("human", """
    <context>
    {context}
    </context>

    사용자 질문: 
    {input}
    """)
])

def get_summarize_prompt(timeline, subtitle):
    """요약 프롬프트 템플릿을 생성합니다."""
    system_prompt = f"""당신은 YouTube 영상의 자막과 타임라인을 분석하여 구조화된 요약을 제공하는 전문가입니다.
    
    다음 규칙을 따라 요약을 작성해주세요:
    1. 전체 영상의 주제를 대표하는 제목을 ### 형식으로 작성하세요.
    2. 전체 내용에 대한 간단한 소개를 작성하세요.
    3. 타임라인의 각 구간별로 다음 형식으로 요약하세요:
    #### 내용에 맞게 수정한 소제목 (타임라인 시간은 표시하지 않음)
    - 핵심 내용 요약 (bullet points)
    - 구체적인 내용 설명
    - 중요한 키워드에는 ** 표시해서 강조 (키워드에 특수문자가 포함된 경우는 ** 표시 제외)
    - 소제목 마다 중간 요약으로 한줄 정리
    4. 마지막에 전체 내용의 핵심 포인트를 3줄로 정리해주세요:
    - ✅ 핵심 요약:
    - 번호 붙여서 3줄 정리
    
    타임라인 정보:
    {timeline}
    
    자막 내용:
    {subtitle}
    """
    
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "위 내용을 요약해주세요.")
    ])