import json
from typing import List, Dict, Tuple


class TemplateManager:
    def __init__(self):
        self.template = (
            "Always cite sources in links only.\n\n"
            "Answer based solely on the following excerpts:\n\n"
        )

    def build_prompt(
        self, excerpts: List[Tuple[str, Dict]], augmented_query: str
    ) -> str:
        prompt = self.template
        for i, (text, meta) in enumerate(excerpts, start=1):
            prompt += f"Excerpt [{i}] (source: {meta['source']} | chunk_id: {meta.get('chunk_id')}):\n{text}\n\n"
        return prompt + f"QUESTION: {augmented_query}\nANSWER:"

    def parse_response(self, response: str) -> Dict:
        try:
            return json.loads(response.strip())
        except json.JSONDecodeError:
            raise ValueError("Failed to parse response.")
