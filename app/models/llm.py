from typing import Any, Dict
import numpy as np

from openai import AsyncOpenAI


class LLM:
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)

    async def embed(self, text: str) -> np.ndarray:
        resp = await self.client.embeddings.create(
            model="text-embedding-3-small", input=[text]
        )
        q_emb = np.array(resp.data[0].embedding, dtype=np.float32)
        return q_emb / np.linalg.norm(q_emb)

    async def generate_response(self, prompt: str, model: str = "gpt-4o-mini", response_format: Dict[str, Any] = None) -> Any:  # type: ignore
        response = await self.client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert helpful and kind assistant. Follow these rules exactly:\n\n"
                        "1. **Answer from provided excerpts only.**\n"
                        "   - Do not use outside information.\n"
                        "   - If you can't answer using only these excerpts, reply:\n"
                        "     “I'm sorry, I don't have enough context to answer that question.”\n\n"
                        "2. **Format your response as JSON** with two fields:\n"
                        '   - `"answer"`: your full answer text.\n'
                        '   - `"links"`: an array of all excerpts you cited.\n'
                        '     Each item in `"links"` must include:\n'
                        '     • `"url"`: the excerpt\'s identifier or link\n'
                        '     • `"text"`: a brief description of what that excerpt says\n\n'
                        "3. **Citing excerpts:**\n"
                        "   - Cite every excerpt that supports any part of your answer.\n"
                        "   - If different excerpts back different points, list them all.\n"
                        "   - When roles are shown (e.g., “(@alice: Course TA)”), treat statements by authoritative roles as higher weight—but still only answer from the text provided."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.5,
            response_format=response_format,  # type: ignore
        )
        return response.choices[0].message
