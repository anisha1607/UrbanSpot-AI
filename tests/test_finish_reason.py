from google.genai import types
print(f"STOP: {types.FinishReason.STOP}")
print(f"OTHER: {types.FinishReason.MAX_TOKENS}")
