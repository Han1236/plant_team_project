# 📢 슈카월드 유튜브 자막 요약 & QnA 서비스  

## 🚀 프로젝트 개요  
**"바쁘다 바빠 현대사회! 영상도 핵심 요약!"**  
이 프로젝트는 **슈카월드의 유튜브 동영상에서 자막을 추출하고 요약한 후, 이를 기반으로 QnA 서비스를 제공하는 것**을 목표로 합니다.  

- **📅 프로젝트 기간:** 2024년 11월 ~ 2025년 2월  
- **🏢 팀명:** Plant  
- **🔧 사용 툴 및 기술:** FastAPI, LangChain, Streamlit, Docker, RAG(Retrieval-Augmented Generation) 

---

## 🎯 주요 기능  
### 1️⃣ 유튜브 영상 자막 추출  
- yt-dlp 라이브러리를 활용하여 **유튜브 영상의 자막과 영상 정보를 자동 추출**합니다.  
- 추출된 자막은 DB에 저장되어 챗봇 대화에서 활용됩니다.  

### 2️⃣ 핵심 내용 요약  
- LLM을 활용하여 **긴 자막을 압축해 핵심 내용을 제공**합니다.  
- 주요 정보만 골라 짧고 명확한 요약을 제공합니다.  

### 3️⃣ QnA 기능  
- RAG을 활용해 사용자가 질문하면 **영상 내용에서 답을 찾아 제공**합니다.  
- 이전 대화 맥락을 기억하여 대화 흐름이 자연스럽게 이어집니다.  

---

## 🎯 서비스 대상  
✔ **빠르게 경제 뉴스를 파악하고 싶은 개인**  
✔ **자막을 빠르고 정확하게 제작하려는 유튜버**  
✔ **영상 내용을 정리해서 학습하고 싶은 학생**  

---

## 🎬 데모 영상  
### 🔹 영상 자막 추출 & 요약 결과 제공  
![Demo](https://github.com/Han1236/plant_team_project/raw/feature/chat_memory/demo/데모영상_1.gif)  

### 🔹 QnA 챗봇 – 질문하고 싶은 영상 선택 후 대화  
![Demo](https://github.com/Han1236/plant_team_project/raw/feature/chat_memory/demo/데모영상_2.gif)  

### 🔹 다른 영상 선택 & 중복 방지 기능 (ChromaDB 활용)  
![Demo](https://github.com/Han1236/plant_team_project/raw/feature/chat_memory/demo/데모영상_3.gif)  

---

## 🔥 이 앱을 사용해보세요!  
### **사용 방법**  
1. 유튜브 비디오 URL을 입력합니다.  
2. 자동으로 자막을 추출하고 DB에 저장합니다.  
3. 핵심 요약을 확인하고, 자유롭게 질문할 수 있습니다.  

### **기대 효과**  
✅ 빠르고 정확한 자막 요약  
✅ 유저 맞춤형 질문 응답  
✅ 정보 소비 시간 절약  

---

## 🛠 기술 스택  
- **Backend:** FastAPI   
- **frontend:** Streamlit   
- **LLM (Large Language Model):** GEMINI  
- **데이터베이스:** ChromaDB  
- **챗봇:** LangChain, RAG (Retrieval-Augmented Generation)  
- **Tools:** Python, Git/Github, Docker  

---