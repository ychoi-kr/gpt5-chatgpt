from pydantic import BaseModel
from agents import Agent

# 지시
INSTRUCTIONS = (
    "당신은 유용한 연구 어시스턴트입니다."
    "쿼리가 주어지면 쿼리에 최적의 답변을 얻기 위해 실행할 웹 검색 세트를 생각해내세요."
    "쿼리할 5개에서 20개의 검색어를 출력하세요."
)

# 웹 검색 아이템
class WebSearchItem(BaseModel):
    reason: str
    "이 검색이 쿼리에 중요한 이유."

    query: str
    "웹 검색에 사용할 검색어."

# 웹 검색 계획
class WebSearchPlan(BaseModel):
    searches: list[WebSearchItem]
    """쿼리에 최적의 답변을 얻기 위해 실행할 웹 검색 리스트."""

# 플래너 에이전트 준비
planner_agent = Agent(
    name="PlannerAgent",
    instructions=INSTRUCTIONS,
    model="gpt-4o",
    output_type=WebSearchPlan,
)