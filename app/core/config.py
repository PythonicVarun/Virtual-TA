import os


class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    EMBED_DIM = 1536  # Dimension for OpenAI text-embedding-3-small
    SIMILARITY_THRESHOLD = 0.35  # Cosine similarity threshold
    FAISS_INDEX_PATH = "model/virtual-ta.faiss"
    METADATA_PATH = "model/metadata.json"
    RESPONSE_FORMAT = {
        "type": "json_schema",
        "json_schema": {
            "schema": "http://json-schema.org/draft-07/schema#",
            "name": "ChatResponse",
            "strict": True,
            "description": "Schema for the Chat Response object returned by the Course Chatbot API.",
            "schema": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The assistant's answer to the user's question.",
                    },
                    "links": {
                        "type": "array",
                        "description": "List of source links referenced in the answer.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "The URL of the source.",
                                },
                                "text": {
                                    "type": "string",
                                    "description": "A short description or title for the source being used for answering the user's question.",
                                },
                            },
                            "required": ["url", "text"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": ["answer", "links"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
