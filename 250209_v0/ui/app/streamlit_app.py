import streamlit as st
from components import header, footer

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
    layout="wide"
)

# 헤더 컴포넌트 로드
# header.show_header()

st.write("# Welcome! 👋")

st.write("""
---
## 슈카월드 Youtube 자막 요약 및 QnA 서비스

이 프로젝트는 **슈카월드의 Youtube 동영상에서 자막을 추출하고 요약하여 이를 기반으로 QnA**를 할 수 있는 서비스를 구현하는 것을 목표로 합니다.

### 주요 기능:
1. **Youtube 동영상 자막 추출**: 유튜브 동영상에서 자막을 자동으로 추출하여 데이터로 변환합니다.
2. **자막 요약**: 추출된 자막을 분석하고 요약하여 핵심적인 내용을 파악할 수 있도록 합니다.
3. **QnA 기능**: 요약된 자막을 기반으로 사용자가 질문을 입력하면, 해당 질문에 대한 답을 자막에서 추출해 제공합니다.

### 프로젝트 목적:
- 슈카월드의 유튜브 동영상을 기반으로, 사용자가 직접 중요한 내용을 요약하거나 QnA를 진행할 수 있도록 도와줍니다.
- 이를 통해 **효율적인 정보 소비와 사용자 맞춤형 학습**을 가능하게 합니다.
  
---
## 이 앱을 사용해보세요!
앱은 위 기능들을 웹 UI를 통해 직관적으로 제공합니다. 사용자는 유튜브 비디오 URL을 입력하고, 동영상의 자막을 요약하거나 그에 대해 질문을 던질 수 있습니다.

### **기대 효과:**
- 빠르고 정확한 자막 요약.
- 유저 맞춤형 질문에 대한 실시간 답변 제공.
""")

# 푸터 컴포넌트 로드
footer.show_footer()