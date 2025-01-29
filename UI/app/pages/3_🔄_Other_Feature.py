import streamlit as st
import pandas as pd
import os
import re

# 페이지 설정
st.set_page_config(
    page_title="추가 기능",
    page_icon="🔄",
)

st.write("# 영상 자막 다운로드")

# test_data 폴더에서 CSV 파일을 읽어 DataFrame으로 표시
file_name = "제2의 엔비디아로 불리는, AI 반도체 최강 기업"
file_path = f"test_data/{file_name}.csv"  # CSV 파일 경로 (예시)
if os.path.exists(file_path):
    # CSV 파일을 DataFrame으로 읽기
    df = pd.read_csv(file_path)

    # DataFrame 표시
    st.write("### DataFrame 내용")
    st.dataframe(df)

    # DataFrame을 CSV 형식으로 변환하여 다운로드 버튼 생성
    csv_data = df.to_csv(index=False, encoding='utf-8-sig')  # 인덱스를 제외하고 CSV로 변환

    st.write("자막 파일을 다운로드하려면 아래 버튼을 클릭하세요.")

    # 다운로드 버튼
    st.download_button(
        label="CSV 파일 다운로드",
        data=csv_data,
        file_name=f"{file_name}.csv",  # 다운로드 시 파일 이름
        mime="text/csv",  # MIME 타입 설정
    )
else:
    st.error(f"test_data 폴더에 '{file_name}.csv' 파일이 없습니다.")

st.markdown('---')

st.write("# CSV파일 전처리")
# 문장 병합 및 끝맺음 처리 함수
def finalize_sentences(texts, max_length=35, min_length=15):
    """
    문장을 병합하며, 끝맺음 처리 및 max_length, min_length 조건에 따라 문장을 나눔.
    중복된 문장을 제거하는 기능 추가
    """
    merged_sentences = []
    temp_sentence = ""
    previous_sentence = ""  # 중복 문장을 체크하기 위한 변수
    
    for text in texts:
        text = re.sub(r'\s+', ' ', text).strip()  # 공백 정리
        
        # 동일한 문장이 나오면 건너뜀
        if text == previous_sentence:
            continue  # 이전 문장과 동일하면 건너뜀
        previous_sentence = text  # 이전 문장을 갱신
        
        temp_sentence += " " + text
        
        # 끝맺음 처리
        temp_sentence = re.sub(r'(합니다|닙니다|입니다|습니다|어요|네요|겠죠|이고요|이에요|어가요|해요|있었)(?![.?!\n])', r'\1.', temp_sentence)
        
        # 문장의 끝이 마침표로 끝나는지 확인
        if temp_sentence.endswith("."):
            # 문장 끝 조건 (최소 길이, 최대 길이 체크)
            if (len(temp_sentence.split()) >= min_length and len(temp_sentence.split()) <= max_length) or len(temp_sentence.split()) >= max_length:
                merged_sentences.append(temp_sentence.strip())
                temp_sentence = ""
        elif len(temp_sentence.split()) >= max_length:
            # 마침표가 없으면 최대 길이가 될 때 문장을 병합
            merged_sentences.append(temp_sentence.strip())
            temp_sentence = ""

    # 남은 문장 추가
    if temp_sentence.strip():
        merged_sentences.append(temp_sentence.strip())
    
    return merged_sentences

# UI에서 파일을 불러오고 처리
if os.path.exists(file_path):
    # CSV 파일을 DataFrame으로 읽기
    df = pd.read_csv(file_path)

    # 섹션별 데이터 분리
    sections = []
    current_section = {'headline': None, 'texts': []}

    for _, row in df.iterrows():
        if row['type'] == 'Section Header' and not pd.isna(row['headline']):
            if current_section['headline'] or current_section['texts']:
                sections.append(current_section)
            current_section = {'headline': row['headline'], 'texts': []}
        elif row['type'] == 'Transcript Segment':
            current_section['texts'].append(row['text'])

    if current_section['headline'] or current_section['texts']:
        sections.append(current_section)

    # 섹션별 문장 병합 및 처리
    structured_data = []
    for section in sections:
        sentences = finalize_sentences(section['texts'])
        structured_data.append({'headline': section['headline'], 'sentences': sentences})

    # 결과를 string으로 변환하여 text_area로 출력
    result_text = ""
    for section in structured_data:
        result_text += f"Headline: {section['headline']}\n"
        result_text += "Sentences:\n"
        for sentence in section['sentences']:
            result_text += f"- {sentence}\n"
        result_text += "\n" + "-"*50 + "\n"

    # 결과를 text_area로 출력
    st.write("### 소제목과 내용으로 구분")
    st.text_area("text", result_text, height=500)
    
    # 결과를 마크다운 형식으로 출력
    for section in structured_data:
        st.markdown(f"#### {section['headline']}")
        for sentence in section['sentences']:
            st.markdown(f"- {sentence}")
        st.markdown("\n" + "---" + "\n")
