import json
import os
import sys
from abc import ABC, abstractmethod
from typing import Dict, Any, List

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class BaseLLMProvider(ABC):
    @abstractmethod
    def generate_plan(self, system_prompt: str, user_input: str) -> str:
        """
        Takes a system prompt and a user input, and returns a JSON string representing the plan items.
        """
        pass

    @abstractmethod
    def refine_parameters(self, original_parameters: Dict[str, Any], feedback: str) -> str:
        """
        Takes the original parameters and user feedback, and returns a JSON string of the refined parameters.
        """
        pass

class GapGPTProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, base_url: str = "https://api.gapgpt.app/v1", model: str = "gapgpt-qwen-3.5"):
        from openai import OpenAI
        api_key = api_key or os.environ.get("GAPGPT_API_KEY", "dummy_key_for_dev")
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def generate_plan(self, system_prompt: str, user_input: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Gapgpt LLM call failed: {str(e)}")
            raise e

    def refine_parameters(self, original_parameters: Dict[str, Any], feedback: str) -> str:
        prompt = f"You previously generated these parameters: {json.dumps(original_parameters)}. The user requested the following change: {feedback}. Return the updated JSON parameters strictly."
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful AI. Output only valid JSON parameters."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Gapgpt LLM call failed for refinement: {str(e)}")
            raise e

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash", integration_verification: bool = False):
        from google import genai
        from google.genai import types
        api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if integration_verification and not api_key:
            raise ValueError("Integration verification mode requires a valid API Key.")
            
        self.client = genai.Client(api_key=api_key)
        self.model = model
        self.integration_verification = integration_verification
        self.config = types.GenerateContentConfig(
            response_mime_type="application/json"
        )

    def _log_request(self, call_type: str, response: Any):
        if self.integration_verification:
            print("\n" + "="*50)
            print(f"--- Gemini API Call: {call_type} ---")
            # Google genai usage metadata
            if hasattr(response, "usage_metadata") and response.usage_metadata:
                print(f"Token Usage: Input={response.usage_metadata.prompt_token_count}, Output={response.usage_metadata.candidates_token_count}, Total={response.usage_metadata.total_token_count}")
            print(f"Model: {self.model}")
            print(f"Raw Response: {response.text}")
            print("="*50 + "\n")

    def generate_plan(self, system_prompt: str, user_input: str) -> str:
        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json"
            )
            response = self.client.models.generate_content(
                model=self.model,
                contents=user_input,
                config=config
            )
            self._log_request("generate_plan", response)
            return response.text
        except Exception as e:
            if self.integration_verification:
                print(f"[FAIL LOUDLY] Gemini generate_plan failed: {str(e)}")
            raise e

    def refine_parameters(self, original_parameters: Dict[str, Any], feedback: str) -> str:
        from google.genai import types
        prompt = f"You previously generated these parameters: {json.dumps(original_parameters)}. The user requested the following change: {feedback}. Return the updated JSON parameters strictly."
        try:
            config = types.GenerateContentConfig(
                system_instruction="You are a helpful AI. Output only valid JSON parameters.",
                response_mime_type="application/json"
            )
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )
            self._log_request("refine_parameters", response)
            return response.text
        except Exception as e:
            if self.integration_verification:
                print(f"[FAIL LOUDLY] Gemini refine_parameters failed: {str(e)}")
            raise e
