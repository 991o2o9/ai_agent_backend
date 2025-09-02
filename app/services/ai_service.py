import json
import asyncio
from typing import List, Dict, Optional
from huggingface_hub import InferenceClient
from app.core.config import settings
from app.core.redis import redis


class AIService:
    def __init__(self):        
        self.client = InferenceClient(
            model=settings.HUGGINGFACE_MODEL,
            token=settings.HUGGINGFACE_API_TOKEN,
        )

    async def generate_response(
        self,
        prompt: str,
        context: List[Dict[str, str]] = None,
        npc_personality: str = "",
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate NPC response using Hugging Face Inference API
        """

        try:
            # Формируем сообщения
            messages = self._build_mistral_messages(prompt, context, npc_personality)

            # Hugging Face работает синхронно → обернём в asyncio.to_thread
            completion = await asyncio.to_thread(
                self.client.chat_completion,
                messages=messages,
                max_tokens=max_tokens or settings.MAX_TOKENS,
                temperature=settings.TEMPERATURE,
                top_p=settings.TOP_P,
            )

            # Извлекаем ответ
            if completion.choices and len(completion.choices) > 0:
                content = completion.choices[0].message["content"]
                if content:
                    return self._clean_response(content)
                else:
                    raise Exception("AI returned empty content")
            else:
                raise Exception("AI service returned no choices")

        except Exception as e:
            raise Exception(f"AI service error: {str(e)}")

    def _build_mistral_messages(
        self,
        prompt: str,
        context: List[Dict[str, str]] = None,
        npc_personality: str = "",
    ) -> List[Dict[str, str]]:
        """
        Build messages in Mistral-compatible chat format
        """
        messages = []

        system_content = f"""You are an NPC in a game with the following personality: {npc_personality}

Instructions:
- Respond naturally and in character
- Keep responses concise (1-3 sentences)
- Be helpful and engaging
- Stay consistent with your personality
- Don't break character
- Respond in the same language as the player's message"""

        messages.append({"role": "system", "content": system_content})

        # Добавляем последние 5 сообщений
        if context:
            for msg in context[-5:]:
                role = "user" if msg.get("is_player", False) else "assistant"
                messages.append({"role": role, "content": msg.get("text", "")})

        # Текущий запрос
        messages.append({"role": "user", "content": prompt})

        return messages

    def _clean_response(self, response: str) -> str:
        """
        Очистка текста от лишних токенов
        """
        cleaned = response.replace("[INST]", "").replace("[/INST]", "").strip()

        if cleaned.startswith("System:"):
            cleaned = cleaned.split("System:", 1)[1].strip()

        if len(cleaned) > 200:
            cleaned = cleaned[:200] + "..."

        return cleaned

    async def get_short_term_memory(self, session_id: str, npc_id: int) -> List[Dict[str, str]]:
        try:
            key = f"memory:session:{session_id}:npc:{npc_id}"
            memory_data = await redis.get(key)
            if memory_data:
                return json.loads(memory_data)
            return []
        except Exception as e:
            print(f"Error getting short-term memory: {e}")
            return []

    async def update_short_term_memory(
        self, session_id: str, npc_id: int, message: str, is_player: bool
    ):
        try:
            key = f"memory:session:{session_id}:npc:{npc_id}"

            memory = await self.get_short_term_memory(session_id, npc_id)

            memory.append(
                {
                    "text": message,
                    "is_player": is_player,
                    "timestamp": asyncio.get_event_loop().time(),
                }
            )

            if len(memory) > 10:
                memory = memory[-10:]

            await redis.setex(key, settings.SHORT_MEMORY_TTL, json.dumps(memory))

        except Exception as e:
            print(f"Error updating short-term memory: {e}")

    async def get_long_term_memory(self, npc_id: int, user_id: int) -> List[Dict[str, str]]:
        return []

    async def rate_limit_check(self, user_id: int) -> bool:
        try:
            minute_key = f"rate_limit:minute:{user_id}"
            hour_key = f"rate_limit:hour:{user_id}"

            minute_count = await redis.get(minute_key)
            if minute_count and int(minute_count) >= settings.MAX_REQUESTS_PER_MINUTE:
                return False

            hour_count = await redis.get(hour_key)
            if hour_count and int(hour_count) >= settings.MAX_REQUESTS_PER_HOUR:
                return False

            await redis.incr(minute_key)
            await redis.incr(hour_key)

            await redis.expire(minute_key, 60)
            await redis.expire(hour_key, 3600)

            return True

        except Exception as e:
            print(f"Error checking rate limit: {e}")
            return True
