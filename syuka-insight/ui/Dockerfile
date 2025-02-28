FROM ubuntu:22.04

# Python 설치
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y curl

# 작업 디렉토리 설정
WORKDIR /app

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 종속성 설치
COPY app/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# 코드 복사
COPY app/ /app/

# 필요한 디렉토리 생성
RUN mkdir -p /app/assets/images

# Streamlit 실행 포트
EXPOSE 8501

# Streamlit 실행 명령
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]

