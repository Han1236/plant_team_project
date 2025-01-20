import pathlib
import textwrap
import os
from dotenv import load_dotenv
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from langchain.memory import ChatMessageHistory

load_dotenv()

GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')

def gen_text(prompt):
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp",
                                    temperature=0.7,
    ) 

    chatprompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """Youtube 영상의 자막을 추출한 내용입니다. 
            전체 내용을 자세히 살펴봐주세요. 
            그리고 보기 좋고 이해하기 쉽도록 내용을 요약해주세요. 
            제목은 전체 내용의 주제로 하고 가장 상단에 출력하세요. 
            요약한 내용은 마크다운 형식으로 출력해주세요.""",
        ),
        ("human", "{input}"),
    ]
    )

    chain = chatprompt | model
    response = chain.invoke(
        {
            "input": prompt,
        }
    )

    return response.content

def gen_chat(prompt, history: ChatMessageHistory):
    model = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp",
                                    temperature=0.7,
    ) 

    chatprompt = ChatPromptTemplate.from_messages(
    [
        ("system", "너는 Youtube 영상 자막을 바탕으로 질의응답을 하는 챗봇이야."),
        ("human", "{input}"),
    ]
    )
    
    chain = chatprompt | model

    # Langchain의 ChatMessageHistory를 Langchain의 메시지 형식으로 변환
    messages = []
    for msg in history.messages:
        if isinstance(msg, SystemMessage):
             messages.append({"role":"system", "content":msg.content})
        elif isinstance(msg, HumanMessage):
            messages.append({"role":"human", "content":msg.content})
        elif isinstance(msg, AIMessage):
            messages.append({"role":"assistant", "content":msg.content})
        
    response = chain.invoke({ "input": prompt, "history": messages})
    return response.content

# Model(name='models/gemini-2.0-flash-exp',
#        base_model_id='',
#        version='2.0',
#        display_name='Gemini 2.0 Flash Experimental',
#        description='Gemini 2.0 Flash Experimental',
#        input_token_limit=1048576,
#        output_token_limit=8192,
#        supported_generation_methods=['generateContent', 'countTokens', 'bidiGenerateContent'],
#        temperature=1.0,
#        max_temperature=2.0,
#        top_p=0.95,
#        top_k=40),