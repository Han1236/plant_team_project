# (1) Ubuntu 최신 버전 기반 PostgreSQL 설치
FROM ubuntu:latest

# 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    postgresql postgresql-contrib \
    && rm -rf /var/lib/apt/lists/*

# 환경 변수 설정
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=mypassword
ENV POSTGRES_DB=mydatabase
ENV PGDATA=/var/lib/postgresql/data

# 데이터 디렉토리 생성 및 권한 설정
RUN mkdir -p /var/lib/postgresql/data && chown -R postgres:postgres /var/lib/postgresql/data

# 초기화 스크립트 복사
COPY init-db.sh /docker-entrypoint-initdb.d/init-db.sh

# 컨테이너 시작 시 PostgreSQL 실행
CMD ["postgres"]
