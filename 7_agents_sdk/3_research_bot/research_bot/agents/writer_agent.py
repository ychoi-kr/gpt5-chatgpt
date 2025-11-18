from pydantic import BaseModel
from agents import Agent

# 지시
INSTRUCTIONS = (
    "당신은 연구 쿼리에 대한 일관성 있는 리포트를 작성하도록 임명된 상급 연구원입니다."
    "원본 쿼리와 연구 조수가 수행한 초기 연구가 제공됩니다."
    "먼저 리포트의 구조와 흐름을 설명하는 리포트 개요를 작성합니다."
    "다음으로 리포트를 생성하여 최종 출력으로 반환합니다."
    "최종 출력은 마크다운 형식이며, 길고 상세해야 합니다."
    "5~10페이지, 최소 1,000단어의 콘텐츠를 목표로 합니다."
)

# 리포트
class ReportData(BaseModel):
    short_summary: str
    """조사 결과를 2~3문장으로 짧게 요약"""

    markdown_report: str
    """최종 보고서"""

    follow_up_questions: list[str]
    """추가 연구를 위한 제안 주제"""

# 작성자 에이전트 준비
writer_agent = Agent(
    name="WriterAgent",
    instructions=INSTRUCTIONS,
    model="o3-mini",
    output_type=ReportData,
)