import asyncio
from .manager import ResearchManager

# main
async def main() -> None:
    query = input("何を研究したいですか?")
    await ResearchManager().run(query)

# mainの実行
if __name__ == "__main__":
    asyncio.run(main())