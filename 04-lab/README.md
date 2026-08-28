# Lab 04 — Weather Agent with Remote MCP Server

A weather agent built with Google ADK that connects to an MCP server via Streamable HTTP transport.

## Architecture

```
┌─────────────────┐   Streamable HTTP    ┌─────────────────┐      REST       ┌─────────────────┐
│   ADK Agent     │ ──────────────────── │   MCP Server    │ ─────────────── │  WeatherAPI.com │
│  (mcp-client)   │   localhost:8085/mcp │  (mcp-server)   │                 │                 │
└─────────────────┘                      └─────────────────┘                 └─────────────────┘
```

## Tools

| Tool | Description |
|------|-------------|
| `get_current_weather(city)` | Get current weather conditions for a city |
| `get_forecast(city, days)` | Get weather forecast (1–3 days) |
| `health_check()` | Verify server is running |

## ADK làm gì trong Lab này?

ADK (Agent Development Kit) đóng vai trò **MCP Client** 
```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  1. KẾT NỐI tới MCP Server qua Streamable HTTP                  │
│     StreamableHTTPConnectionParams(url="localhost:8085/mcp")    │
│                                                                 │
│  2. KHÁM PHÁ tools tự động (list_tools)                         │
│     McpToolset → tự hỏi server "anh có tool gì?"                │
│     → nhận về: get_current_weather, get_forecast, health_check  │
│                                                                 │
│  3. TRUYỀN tools cho LLM (Gemini)                               │
│     Agent(model="gemini-2.5-flash", tools=[weather_tools])      │
│     → Gemini biết nó có thể gọi 3 tools trên                    │
│                                                                 │
│  4. ĐIỀU PHỐI vòng lặp Function Calling                         │
│     User hỏi → Gemini chọn tool → ADK gọi MCP Server            │
│     → nhận kết quả → đưa lại cho Gemini tổng hợp                │
│                                                                 │
│  5. CUNG CẤP giao diện web (adk web)                            │
│     → http://localhost:8000 để chat với agent                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

So với bài 02 (viết client thủ công bằng `mcp.ClientSession`), ADK giúp bạn **không phải viết vòng lặp function calling thủ công** nữa. Toàn bộ luồng list_tools → model quyết định → call_tool → model tổng hợp được ADK xử lý tự động.

## Setup (Windows — dùng chung .venv của repo)

> Bản này đã đổi model agent sang **OpenAI qua LiteLLM** (`openai/gpt-4o-mini`)
> thay cho Gemini, và dùng chung `..\..\.venv` thay vì `uv sync` từng thư mục.

### 1. MCP Server (terminal 1)

```powershell
cd 04-lab\mcp-server
# điền WEATHERAPI_KEY vào file .env (key free tại https://www.weatherapi.com/)
..\..\.venv\Scripts\python.exe weather.py
```

Server chạy tại `http://localhost:8085/mcp`. Thêm `--stdio` để chạy chế độ stdio.

### 2. ADK Agent (terminal 2)

`04-lab/mcp-client/.env` đã có sẵn `OPENAI_API_KEY` (lấy từ bước 1) và `MCP_SERVER_URL`.

Chạy nhanh không cần trình duyệt:

```powershell
cd 04-lab\mcp-client
..\..\.venv\Scripts\python.exe test_agent.py "Thời tiết Hà Nội hôm nay?"
```

Hoặc giao diện web ADK:

```powershell
..\..\.venv\Scripts\adk.exe web
```

Mở http://localhost:8000, chọn `weather_agent`, hỏi về thời tiết.

## Configuration

| Variable | Where | Description |
|----------|-------|-------------|
| `WEATHERAPI_KEY` | mcp-server/.env | API key từ weatherapi.com |
| `OPENAI_API_KEY` | mcp-client/.env | Key OpenAI cho agent (qua LiteLLM) |
| `LITELLM_MODEL` | mcp-client/.env | Model agent (mặc định `openai/gpt-4o-mini`) |
| `MCP_SERVER_URL` | mcp-client/.env | URL MCP server (mặc định `http://localhost:8085/mcp`) |
| `PORT` | mcp-server (env) | Override cổng server (mặc định 8085) |
