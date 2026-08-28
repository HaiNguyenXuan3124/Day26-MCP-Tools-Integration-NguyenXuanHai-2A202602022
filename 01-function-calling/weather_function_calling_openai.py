"""Minh hoạ FUNCTION CALLING thuần với OpenAI SDK.

Bản song song của `weather_function_calling.py` (Gemini) — cùng tool `get_weather`,
schema định nghĩa thủ công, app tự thực thi tool, model chỉ QUYẾT ĐỊNH gọi tool nào.

Cách chạy:
    pip install -r ../requirements.txt
    # thêm dòng OPENAI_API_KEY=sk-... vào file .env
    python weather_function_calling_openai.py
"""

import json
import os
import sys

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

if not os.getenv("OPENAI_API_KEY"):
    raise SystemExit(
        "Chưa có API key. Thêm dòng OPENAI_API_KEY=sk-... vào file .env "
        "(lấy key tại https://platform.openai.com/api-keys)"
    )

from openai import OpenAI

client = OpenAI()

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

SYSTEM_INSTRUCTION = (
    "Bạn là trợ lý thời tiết thân thiện, trả lời bằng tiếng Việt tự nhiên. "
    "Dùng emoji phù hợp (🌧️ 🌤️ 💨 💧). "
    "Tóm tắt ngắn gọn, dễ hiểu, và đưa ra lời khuyên thực tế "
    "(ví dụ: mang ô, mặc áo mỏng, ...)."
)

# 1. App tự định nghĩa schema của tool (format OpenAI)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Lấy thời tiết hiện tại của một thành phố",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Tên thành phố"}
                },
                "required": ["city"],
            },
        },
    }
]


# 2. App tự thực thi tool (trong thực tế sẽ gọi API thời tiết thật)
def get_weather(city: str) -> str:
    """Trả về thời tiết (mock) của *city*. Dùng làm tool cho model."""
    mock_data = {
        "Hà Nội": {
            "nhiệt_độ": "29°C",
            "thời_tiết": "trời mưa nhẹ",
            "độ_ẩm": "82%",
            "gió": {"hướng": "Đông Nam", "tốc_độ": "12 km/h"},
        },
        "Hồ Chí Minh": {
            "nhiệt_độ": "33°C",
            "thời_tiết": "mưa rào",
            "độ_ẩm": "75%",
            "gió": {"hướng": "Tây Nam", "tốc_độ": "15 km/h"},
        },
        "Đà Nẵng": {
            "nhiệt_độ": "30°C",
            "thời_tiết": "nhiều mây",
            "độ_ẩm": "78%",
            "gió": {"hướng": "Đông", "tốc_độ": "10 km/h"},
        },
    }
    default = {"nhiệt_độ": "28°C", "thời_tiết": "không có dữ liệu chi tiết"}
    return json.dumps({"city": city, **mock_data.get(city, default)}, ensure_ascii=False)


def run(prompt: str) -> str:
    """Gửi *prompt* tới OpenAI, tự động xử lý function calling và trả về câu trả lời cuối."""
    messages = [
        {"role": "system", "content": SYSTEM_INSTRUCTION},
        {"role": "user", "content": prompt},
    ]

    # 3. Gọi model — model quyết định có gọi tool hay không
    resp = client.chat.completions.create(
        model=MODEL, messages=messages, tools=TOOLS
    )
    msg = resp.choices[0].message

    # 4. Vòng lặp: nếu model yêu cầu tool, app TỰ THỰC THI rồi đưa kết quả trả lại
    while msg.tool_calls:
        messages.append(msg)  # phản hồi của model (kèm tool_calls) vào lịch sử

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            print(f"  [model yêu cầu] {tc.function.name}({args})")
            result = get_weather(**args)  # <-- app chạy, không phải model
            print(f"  [app thực thi]  -> {result}")
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )

        resp = client.chat.completions.create(
            model=MODEL, messages=messages, tools=TOOLS
        )
        msg = resp.choices[0].message

    # 5. Model tổng hợp câu trả lời cuối
    return msg.content


if __name__ == "__main__":
    question = "Thời tiết Hà Nội và Đà Nẵng hôm nay thế nào?"
    print(f"User: {question}\n")
    print("Trả lời:", run(question))
