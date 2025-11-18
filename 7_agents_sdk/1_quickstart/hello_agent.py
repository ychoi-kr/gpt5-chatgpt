from agents import Agent, Runner

# 에이전트 생성
agent = Agent(
    name="Assistant",
    instructions="당신은 영어를 한국어로 번역하는 어시스턴트입니다."
)

# 에이전트 실행
result = Runner.run_sync(agent, "I am a cat.")
print(result.final_output)