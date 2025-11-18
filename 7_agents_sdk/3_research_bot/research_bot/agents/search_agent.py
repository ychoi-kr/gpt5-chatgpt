from agents import Agent, WebSearchTool
from agents.model_settings import ModelSettings

# 지시
INSTRUCTIONS = (
    "당신은 연구 조수입니다. 검색어가 주어지면 그 검색어로 웹을 검색하고 결과의 간결한 요약을 작성합니다."
    "요약은 2~3단락, 300단어 미만이어야 합니다."
    "요점을 파악하세요. 간결하게 작성합니다. 완전한 문장이나 올바른 문법일 필요는 없습니다."
    "이것은 리포트를 정리하는 사람이 읽는 것이므로 요점을 파악하고 불필요한 부분은 무시하는 것이 중요합니다."
    "요약 자체 외의 코멘트는 포함하지 마세요."
)

# 검색 에이전트 준비
search_agent = Agent(
    name="SearchAgent",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool()],
    model_settings=ModelSettings(tool_choice="required"),
)