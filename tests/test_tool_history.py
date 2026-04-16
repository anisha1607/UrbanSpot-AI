from agents.gemini_client import GeminiChatSession, TextBlock, ToolUseBlock
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing GeminiChatSession with Tool History...")

session = GeminiChatSession()

# Mock a conversation history that includes a tool use and a tool result
messages = [
    {"role": "user", "content": "What is the population of Manhattan?"},
    {
        "role": "assistant", 
        "content": [
            ToolUseBlock(id="call_1", name="check_data_quality", input={"neighborhood": "Manhattan"})
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": "call_1",
                "tool_name": "check_data_quality",
                "content": '{"population": 1600000, "status": "GOOD"}'
            }
        ]
    }
]

try:
    response = session.create_message(
        system="You are a helpful data analyst. Use the tool results provided in the history.",
        messages=messages
    )
    print("🚀 SUCCESS! History with tool results handled correctly.")
    print(f"Final Response: {response.content[0].text}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
