def format_subtitle(subtitle_text):
    """자막 텍스트를 포맷팅합니다."""
    if not subtitle_text:
        return "자막이 없습니다."
    
    # # 너무 긴 자막은 잘라내기
    # if len(subtitle_text) > 10000:
    #     return subtitle_text[:10000] + "...(생략)"
    
    return subtitle_text

def format_summary(summary_text):
    """요약 텍스트를 포맷팅합니다."""
    if not summary_text:
        return "요약 정보가 없습니다."
    
    return summary_text