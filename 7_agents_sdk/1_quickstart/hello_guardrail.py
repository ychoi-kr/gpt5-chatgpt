from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner
from pydantic import BaseModel
import asyncio
import argparse

# 数学家庭教師エージェントの定義
math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="数学の質問に特化したエージェント",
    instructions=(
        "あなたは数学の問題を手助けします。"
        "各ステップで論理的な説明を行い、例を含めてください。"
    ),
)

# 歴史家庭教師エージェントの定義
history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="歴史の質問に特化したエージェント",
    instructions=(
        "あなたは歴史に関する質問を手助けします。"
        "重要な出来事や背景を明確に説明してください。"
    ),
)

# 宿題に関する質問かどうかを判断するモデル
class HomeworkOutput(BaseModel):
    is_homework: bool   # 質問が数学・歴史かどうか（True＝許可）
    reasoning: str      # その判断理由（説明責任用）

# ガードレールエージェントの定義
guardrail_agent = Agent(
    name="Guardrail check",
    instructions="数学または歴史に関する質問かどうか確認してください。",
    output_type=HomeworkOutput,
)

# ガードレール関数の定義
async def homework_guardrail(ctx, agent, input_data):
    # ガードレールエージェントで判定
    result = await Runner.run(guardrail_agent, input_data, context=ctx.context)
    final_output = result.final_output_as(HomeworkOutput)

    # GuardrailFunctionOutput型で返す
    return GuardrailFunctionOutput(
        output_info=final_output, # ロギング用に判定結果を保持
        tripwire_triggered=not final_output.is_homework  # True なら“地雷”＝拒否
    )

# トリアージエージェントの定義
triage_agent = Agent(
    name="Triage Agent",
    instructions="ユーザーの質問が宿題に関するものかを判断し、適切なエージェントを選択してください。",
    handoffs=[history_tutor_agent, math_tutor_agent],
    input_guardrails=[
        InputGuardrail(guardrail_function=homework_guardrail), # ガードレール
    ],
)

# main
async def main(prompts: list[str]):
    for prompt in prompts:
        try:
            result = await Runner.run(triage_agent, prompt)
            print(result.final_output)
        except Exception as e:
            print("エラー:", e)

# mainの実行
if __name__ == "__main__":
    # 引数
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "prompts",
        nargs="+",
        help="質問文",
    )
    args = parser.parse_args()

    # mainの実行
    asyncio.run(main(args.prompts))