from agents import Agent, Runner

# エージェントの作成
agent = Agent(
    name="Assistant", 
    instructions="あなたは英語を日本語に翻訳するアシスタントです。"
)

# エージェントの実行
result = Runner.run_sync(agent, "I am a cat.")
print(result.final_output)