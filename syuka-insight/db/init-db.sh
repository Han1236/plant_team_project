#!/bin/bash
set -e

echo "===== PostgreSQL 초기 설정 실행 중 ====="

#!/bin/bash
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE TABLE IF NOT EXISTS videos (
        id SERIAL PRIMARY KEY,
        video_id VARCHAR(255) UNIQUE NOT NULL,
        title TEXT,
        channel TEXT,
        upload_date DATE,
        duration INTEGER,
        view_count BIGINT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS subtitles (
        id SERIAL PRIMARY KEY,
        video_id VARCHAR(255) NOT NULL,
        start_time FLOAT NOT NULL,
        end_time FLOAT NOT NULL,
        subtitle_text TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        CONSTRAINT fk_video
            FOREIGN KEY (video_id)
            REFERENCES videos(video_id)
            ON DELETE CASCADE
    );
EOSQL


echo "===== PostgreSQL 초기 설정 완료 ====="
