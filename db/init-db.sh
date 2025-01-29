#!/bin/bash
set -e

echo "===== PostgreSQL 초기 설정 실행 중 ====="

psql -U postgres -c "CREATE DATABASE mydatabase;"
psql -U postgres -c "ALTER USER postgres WITH PASSWORD 'mypassword';"

echo "===== 초기 데이터 입력 ====="
psql -U postgres -d mydatabase -c "
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL
    );
"

echo "===== PostgreSQL 초기 설정 완료 ====="
