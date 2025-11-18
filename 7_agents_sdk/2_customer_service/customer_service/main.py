from __future__ import annotations as _annotations
import asyncio
import random
import uuid
from pydantic import BaseModel
from agents import (
    Agent,
    HandoffOutputItem,
    ItemHelpers,
    MessageOutputItem,
    RunContextWrapper,
    Runner,
    ToolCallItem,
    ToolCallOutputItem,
    TResponseInputItem,
    function_tool,
    handoff,
    trace,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX

# 항공사 에이전트 컨텍스트
class AirlineAgentContext(BaseModel):
    passenger_name: str | None = None  # 승객명
    confirmation_number: str | None = None  # 확인 번호
    seat_number: str | None = None  # 좌석 번호
    flight_number: str | None = None  # 항공편 번호

# FAQ 툴 준비
@function_tool(
    name_override="faq_lookup_tool",
    description_override="FAQ에 관한 질문의 답변을 제공합니다."
)
async def faq_lookup_tool(question: str) -> str:
    if "가방" in question or "짐" in question or "수하물" in question:
        return (
            "비행기에는 가방 1개를 기내 반입할 수 있습니다."
            "무게는 50파운드 이하, 크기는 22인치 x 14인치 x 9인치여야 합니다."
        )
    elif "좌석" in question or "비행기" in question:
        return (
            "비행기에는 120석이 있습니다."
            "비즈니스 클래스 좌석은 22석, 이코노미 클래스 좌석은 98석입니다."
            "비상구는 4열과 16열에 있습니다."
            "5열부터 8열까지는 이코노미 플러스로, 다리 공간에 여유가 있습니다."
        )
    elif "WiFi" in question or "Wi-Fi" in question or "와이파이" in question:
        return "비행기에는 무료 Wi-Fi가 있습니다. Airline-Wifi에 참여하세요"
    return "죄송합니다만, 그 질문의 답을 알 수 없습니다."

# 좌석 업데이트 툴 준비
@function_tool
async def update_seat(
    context: RunContextWrapper[AirlineAgentContext], confirmation_number: str, new_seat: str
) -> str:
    """
    지정된 확인 번호의 좌석을 업데이트합니다.

    Args:
        confirmation_number: 항공편 확인 번호
        new_seat: 업데이트할 새 좌석
    """
    # 고객 입력에 기반하여 컨텍스트 업데이트
    context.context.confirmation_number = confirmation_number
    context.context.seat_number = new_seat

    # 항공편 번호가 설정되어 있는지 확인
    assert context.context.flight_number is not None, "항공편 번호는 필수입니다."
    return f"확인 번호 {confirmation_number}의 좌석을 {new_seat}으로 업데이트했습니다."

# 핸드오프 시 호출되는 훅 준비
async def on_seat_booking_handoff(context: RunContextWrapper[AirlineAgentContext]) -> None:
    flight_number = f"FLT-{random.randint(100, 999)}"
    context.context.flight_number = flight_number


# FAQ 에이전트 준비
faq_agent = Agent[AirlineAgentContext](
    name="FAQ Agent",
    handoff_description="항공사에 관한 질문에 답해주는 친절한 에이전트입니다.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    당신은 FAQ 에이전트입니다. 고객과 대화 중일 때는 트리아지 에이전트로부터 전달받았을 가능성이 있습니다.
    다음 절차에 따라 고객을 지원합니다.
    # 절차
    1. 고객이 마지막으로 물은 질문을 파악합니다.
    2. faq_lookup_tool을 사용하여 질문에 답합니다. 자신의 지식에 의존하지 마세요.
    3. 질문에 답할 수 없으면 트리아지 에이전트로 전달합니다.""",
    tools=[faq_lookup_tool],
)

# 좌석 예약 에이전트 준비
seat_booking_agent = Agent[AirlineAgentContext](
    name="Seat Booking Agent",
    handoff_description="항공편 좌석을 업데이트할 수 있는 편리한 에이전트입니다.",
    instructions=f"""{RECOMMENDED_PROMPT_PREFIX}
    당신은 좌석 예약 에이전트입니다. 고객과 대화 중일 때는 트리아지 에이전트로부터 전달받았을 가능성이 있습니다.
    다음 절차에 따라 고객을 지원합니다.
    # 절차
    1. 확인 번호를 묻습니다.
    2. 고객에게 희망하는 좌석 번호를 묻습니다.
    3. update_seat을 사용하여 항공편 좌석을 업데이트합니다.
    고객이 절차와 관계없는 질문을 하면 트리아지 에이전트로 전달합니다. """,
    tools=[update_seat],
)

# 트리아지 에이전트 준비
triage_agent = Agent[AirlineAgentContext](
    name="Triage Agent",
    handoff_description="고객의 요청을 적절한 에이전트에게 위임할 수 있는 트리아지 에이전트입니다.",
    instructions=(
        f"{RECOMMENDED_PROMPT_PREFIX} "
        "당신은 유용한 트리아지 에이전트입니다. 질문을 다른 적절한 에이전트에게 위임할 수 있습니다."
    ),
    handoffs=[
        faq_agent,
        handoff(agent=seat_booking_agent, on_handoff=on_seat_booking_handoff),
    ],
)

# 상호 핸드오프
faq_agent.handoffs.append(triage_agent)
seat_booking_agent.handoffs.append(triage_agent)

# main
async def main():
    current_agent: Agent[AirlineAgentContext] = triage_agent # 처음은 트리아지 에이전트
    input_items: list[TResponseInputItem] = []
    context = AirlineAgentContext()

    # 대화 ID에 랜덤 UUID 사용
    conversation_id = uuid.uuid4().hex[:16]

    while True:
        # 메시지 입력
        user_input = input("메시지를 입력: ")
        with trace("Customer service", group_id=conversation_id):
            # 에이전트 실행
            input_items.append({"role": "user", "content": user_input})
            result = await Runner.run(current_agent, input_items, context=context)

            # 출력
            for new_item in result.new_items:
                agent_name = new_item.agent.name
                if isinstance(new_item, MessageOutputItem):
                    print(f"{agent_name}: {ItemHelpers.text_message_output(new_item)}")
                elif isinstance(new_item, HandoffOutputItem):
                    print(
                        f"Handed off from {new_item.source_agent.name} to {new_item.target_agent.name}"
                    )
                elif isinstance(new_item, ToolCallItem):
                    print(f"{agent_name}: Calling a tool")
                elif isinstance(new_item, ToolCallOutputItem):
                    print(f"{agent_name}: Tool call output: {new_item.output}")
                else:
                    print(f"{agent_name}: Skipping item: {new_item.__class__.__name__}")
            input_items = result.to_input_list()
            current_agent = result.last_agent

# main 실행
if __name__ == "__main__":
    asyncio.run(main())
