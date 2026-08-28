"""Test nhanh (không cần trình duyệt) — chạy 1 câu hỏi qua agent + MCP tools.

    cd 04-lab/mcp-client
    ..\\..\\.venv\\Scripts\\python.exe test_agent.py "Thời tiết Hà Nội hôm nay?"
"""
import asyncio
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

from google.adk.runners import InMemoryRunner
from google.genai import types

from weather_agent import root_agent


async def main() -> None:
    question = sys.argv[1] if len(sys.argv) > 1 else "Thời tiết Hà Nội hôm nay thế nào?"
    runner = InMemoryRunner(agent=root_agent, app_name="weather")
    session = await runner.session_service.create_session(
        app_name="weather", user_id="u1"
    )
    print(f"User: {question}\n")
    async for event in runner.run_async(
        user_id="u1",
        session_id=session.id,
        new_message=types.Content(role="user", parts=[types.Part(text=question)]),
    ):
        for part in (event.content.parts if event.content else []):
            if part.function_call:
                print(f"  [tool call] {part.function_call.name}({dict(part.function_call.args)})")
            if part.function_response:
                print(f"  [tool result] {str(part.function_response.response)[:200]}")
            if part.text:
                print(f"\nAgent: {part.text}")


if __name__ == "__main__":
    asyncio.run(main())
