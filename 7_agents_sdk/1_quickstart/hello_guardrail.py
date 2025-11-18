from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from pydantic import BaseModel
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

# 숙제에 관한 질문인지 판단하는 모델
class HomeworkOutput(BaseModel):
    is_homework: bool   # 질문이 수학·역사인지 여부(True=허용)
    reasoning: str      # 그 판단 이유(설명 책임용)

# 가드레일 에이전트 정의
guardrail_agent = Agent(
    name="Guardrail check",
    instructions="수학 또는 역사에 관한 질문인지 확인하세요.",
    output_type=HomeworkOutput,
)

# 가드레일 함수 정의
async def homework_guardrail(ctx, agent, input_data):
    # 가드레일 에이전트로 판정
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)

    # GuardrailFunctionOutput 타입으로 반환
    return GuardrailFunctionOutput(
        output_info=final_output, # 로깅용으로 판정 결과 보유
        tripwire_triggered=not final_output.is_homework  # True이면 "지뢰"=거부
    )

# 트리아지 에이전트 정의
triage_agent = Agent(
    name="Triage Agent",
    instructions="사용자의 질문이 숙제에 관한 것인지 판단하고 적절한 에이전트를 선택하세요.",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail), # 가드레일
    ],
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