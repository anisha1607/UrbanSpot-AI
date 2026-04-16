"""
LLM Client Wrapper (Unified Google GenAI SDK)
=====================================
Provides a unified interface for calling LLM models via the new
google-genai SDK, supporting both Vertex AI and AI Studio backends.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional, Union
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration from .env
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "csee4121-s26")
LOCATION = os.getenv("GCP_LOCATION", "us-central1")
DEFAULT_MODEL_NAME = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")
API_KEY = os.getenv("GOOGLE_API_KEY")

# Initialize the GenAI Client (Standard Mode via API Key)
client = genai.Client(
    api_key=API_KEY
)

DEFAULT_MODEL = DEFAULT_MODEL_NAME

def anthropic_tools_to_gemini(tools: List[Dict[str, Any]]) -> List[types.Tool]:
    """
    Convert Anthropic-style tool definitions to Google GenAI Tool objects.
    """
    func_declarations = []
    for tool in tools:
        # Standardize the schema for Gemini
        parameters = tool.get("input_schema", {
            "type": "OBJECT",
            "properties": {},
            "required": []
        })
        
        # Google GenAI SDK expects "type" in uppercase for JSON schema
        if "type" in parameters:
            parameters["type"] = parameters["type"].upper()
            
        func_declarations.append(
            types.FunctionDeclaration(
                name=tool["name"],
                description=tool.get("description", ""),
                parameters=parameters
            )
        )
    return [types.Tool(function_declarations=func_declarations)]

class TextBlock:
    def __init__(self, text):
        self.type = "text"
        self.text = text

class ToolUseBlock:
    def __init__(self, id, name, input, thought_signature=None):
        self.type = "tool_use"
        self.id = id
        self.name = name
        self.input = input
        self.thought_signature = thought_signature

class GeminiChatSession:
    """
    A chat session wrapper that provides an Anthropic-like interface.
    """
    
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model_name = model
            
    def create_message(
        self,
        system: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        max_tokens: int = 4096,
    ) -> "GeminiResponse":
        """
        Create a message using the new Google GenAI SDK.
        """
        gemini_tools = anthropic_tools_to_gemini(tools) if tools else None
        
        # Prepare content
        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            parts = []
            
            raw_content = msg["content"]
            if isinstance(raw_content, str):
                parts.append(types.Part(text=raw_content))
            elif isinstance(raw_content, list):
                for item in raw_content:
                    if hasattr(item, "type"):
                        if item.type == "text":
                            parts.append(types.Part(text=item.text))
                        elif item.type == "tool_use":
                            parts.append(types.Part(
                                function_call=types.FunctionCall(
                                    name=item.name,
                                    args=item.input
                                ),
                                thought_signature=getattr(item, 'thought_signature', None)
                            ))
                    elif isinstance(item, dict) and item.get("type") == "tool_result":
                        parts.append(types.Part(
                            function_response=types.FunctionResponse(
                                name=item["tool_name"],
                                response={"result": item["content"]}
                            )
                        ))
                    elif isinstance(item, str):
                        parts.append(types.Part(text=item))
            
            if parts:
                contents.append(types.Content(role=role, parts=parts))
            
        config = types.GenerateContentConfig(
            system_instruction=system,
            tools=gemini_tools,
            temperature=0.2,
            max_output_tokens=max_tokens,
        )

        response = self._call_with_retry(contents, config)
        return GeminiResponse(response)
    
    def _call_with_retry(self, contents, config, max_retries=4):
        """Call Gemini with robust retry logic."""
        for attempt in range(max_retries):
            try:
                return client.models.generate_content(
                    model=self.model_name,
                    contents=contents,
                    config=config
                )
            except Exception as e:
                error_msg = str(e).upper()
                if any(x in error_msg for x in ["503", "UNAVAILABLE", "429", "RESOURCE_EXHAUSTED", "BUSY"]):
                    wait_time = 15 * (attempt + 1)
                    print(f"⏳ Gemini Server Busy (Attempt {attempt+1}/{max_retries}). Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"❌ Gemini SDK Error: {str(e)}")
                    if any(x in error_msg for x in ["401", "403", "MUTUALLY EXCLUSIVE"]):
                        raise
        
        return client.models.generate_content(
            model=self.model_name,
            contents=contents,
            config=config
        )

class GeminiResponse:
    """
    Simplified response wrapper for agent compatibility.
    """
    def __init__(self, raw_response):
        self.raw_response = raw_response
        self.content = []
        self.stop_reason = "end_turn" # DEFAULT
        
        try:
            if not raw_response.candidates:
                self.stop_reason = "end_turn"
                return

            candidate = raw_response.candidates[0]
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.function_call:
                        self.stop_reason = "tool_use"
                        self.content.append(ToolUseBlock(
                            id=f"call_{part.function_call.name}_{int(time.time() * 1000)}",
                            name=part.function_call.name,
                            input=part.function_call.args,
                            thought_signature=part.thought_signature # Field is on the part
                        ))
                    elif part.text is not None:
                        self.content.append(TextBlock(text=part.text))
            
            # STANDARD MAP
            # If we already detected tool_use above, keep it.
            # Otherwise, use Gemini's finish_reason to detect finalization.
            finish_reason = str(candidate.finish_reason).upper()
            if self.stop_reason != "tool_use":
                self.stop_reason = "end_turn" # Standard return for all terminal states
                
        except Exception as e:
            self.stop_reason = "end_turn"
            self.content.append(TextBlock(text=""))
