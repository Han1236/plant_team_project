from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from models.youtube import Video, Subtitle

async def save_video_info(db: AsyncSession, video_id: str, info: dict, subtitle: str):
    """DB에 영상 정보 및 자막을 저장합니다."""
    # videos 테이블에 영상 정보 저장
    result = await db.execute(select(Video).where(Video.video_id == video_id))
    video_obj = result.scalars().first()
    
    if not video_obj:
        try:
            upload_date = datetime.strptime(info.get("upload_date", ""), "%Y%m%d").date()
        except Exception:
            upload_date = None
            
        video_obj = Video(
            video_id=video_id,
            title=info.get("title", ""),
            channel=info.get("channel", ""),
            upload_date=upload_date,
            duration=int(info.get("duration", 0)),
            view_count=int(info.get("view_count", 0)),
        )
        db.add(video_obj)
        await db.commit()
    
    # subtitles 테이블에 자막 정보 저장
    if subtitle and subtitle.strip() and subtitle != "자막이 없습니다.":
        result = await db.execute(select(Subtitle).where(Subtitle.video_id == video_id))
        subtitle_obj = result.scalars().first()
        
        if not subtitle_obj:
            subtitle_obj = Subtitle(
                video_id=video_id,
                start_time=0,
                end_time=0,
                subtitle_text=subtitle
            )
            db.add(subtitle_obj)
            await db.commit()