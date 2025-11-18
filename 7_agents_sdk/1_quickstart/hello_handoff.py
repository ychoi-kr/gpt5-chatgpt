from agents import Agent, Runner
import asyncio
import argparse

# 수학 튜터 에이전트 정의
math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="수학 질문에 특화된 에이전트",
    instructions=(
        "당신은 수학 문제를 도와줍니다."
        "각 단계에서 논리적인 설명을 하고 예시를 포함하세요."
    ),
)

# 역사 튜터 에이전트 정의
history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="역사 질문에 특화된 에이전트",
    instructions=(
        "당신은 역사에 관한 질문을 도와줍니다."
        "중요한 사건과 배경을 명확하게 설명하세요."
    ),
)

# 트리아지 에이전트 정의
triage_agent = Agent(
    name="Triage Agent",
    instructions="사용자의 질문이 숙제에 관한 것인지 판단하고 적절한 에이전트를 선택하세요.",
    handoffs=[history_tutor_agent, math_tutor_agent], # 핸드오프
)

# main
async def main(prompts: list[str]):
    for prompt in prompts:
        try:
            result = await Runner.run(triage_agent, prompt)
            print(result.final_output)
        except Exception as e:
            print("오류:", e)

# main 실행
if __name__ == "__main__":
    # 인자
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "prompts",
        nargs="+",
        help="질문문",
    )
    args = parser.parse_args()

    # main 실행
    asyncio.run(main(args.prompts))