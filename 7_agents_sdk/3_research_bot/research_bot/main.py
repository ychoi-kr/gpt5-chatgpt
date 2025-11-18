import asyncio
from .manager import ResearchManager

# main
async def main() -> None:
    query = input("무엇을 연구하고 싶으세요?")
    await ResearchManager().run(query)

# main 실행
if __name__ == "__main__":
    asyncio.run(main())