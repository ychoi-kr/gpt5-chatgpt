from agents import Agent, Runner
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

# トリアージエージェントの定義
triage_agent = Agent(
    name="Triage Agent",
    instructions="ユーザーの質問が宿題に関するものかを判断し、適切なエージェントを選択してください。",
    handoffs=[history_tutor_agent, math_tutor_agent], # ハンドオフ
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