FROM ubuntu:22.04

# Python 설치
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y curl

# 작업 디렉토리 설정
WORKDIR /app

# 종속성 설치
COPY app/requirements.txt . 
RUN pip3 install --no-cache-dir -r requirements.txt

# 코드 복사
COPY app/ /app/ 

# PYTHONPATH 환경변수
ENV PYTHONPATH="${PYTHONPATH}:/app"

# FastAPI 실행 포트
EXPOSE 8000

# FastAPI 실행 명령
CMD ["uvicorn", "web_server_main:app", "--host", "0.0.0.0", "--port", "8000"]