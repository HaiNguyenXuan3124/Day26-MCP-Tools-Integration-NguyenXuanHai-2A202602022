"""Weather Agent - Google ADK + MCP server (Streamable HTTP).

Model chạy qua LiteLLM (OpenAI) thay cho Gemini để dùng chung OPENAI_API_KEY.
Đổi model bằng biến môi trường LITELLM_MODEL (mặc định: openai/gpt-4o-mini).
"""
import logging
import os

from dotenv import load_dotenv

load_dotenv()  # đọc OPENAI_API_KEY, MCP_SERVER_URL, LITELLM_MODEL từ .env

from google.adk import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StreamableHTTPConnectionParams,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8085/mcp")
MODEL = os.getenv("LITELLM_MODEL", "openai/gpt-4o-mini")

logger.info(f"🌐 Weather agent | model={MODEL} | MCP={MCP_SERVER_URL}")

try:
    connection_params = StreamableHTTPConnectionParams(
        url=MCP_SERVER_URL,
        timeout=30.0,
    )
    weather_tools = McpToolset(connection_params=connection_params)
    logger.info("✅ MCP toolset created")

    root_agent = Agent(
        name="weather_agent",
        model=LiteLlm(model=MODEL),
        instruction=(
            "Bạn là trợ lý thời tiết. Dùng các tool get_current_weather, "
            "get_forecast, health_check để trả lời. Trả lời bằng tiếng Việt, "
            "ngắn gọn, kèm lời khuyên thực tế."
        ),
        tools=[weather_tools],
    )
    logger.info("✅ Weather agent initialized with remote MCP tools")

except Exception as e:
    logger.error(f"❌ Failed to init agent with MCP tools: {e}")
    import traceback

    traceback.print_exc()
    root_agent = Agent(
        name="weather_agent",
        model=LiteLlm(model=MODEL),
        instruction="Bạn là trợ lý thời tiết (chưa kết nối được MCP server).",
    )
