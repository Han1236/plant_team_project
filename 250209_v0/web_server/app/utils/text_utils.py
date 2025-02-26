# def format_view_count(view_count):
#     """
#     조회수를 한국어 형식에 맞춰 변환합니다.
#     """
#     view_count = int(view_count)

#     if view_count < 1000:
#         return f"{view_count}회"
#     elif view_count < 10000:
#         thousands = view_count / 1000
#         return f"{thousands:.1f}천회" # 소수점 한자리까지 표시
#     else:
#         mans = view_count / 10000
#         return f"{int(mans)}만회" # 만 단위는 정수로 표시