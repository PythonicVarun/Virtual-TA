import json
from fastapi import APIRouter, HTTPException

from app.core.config import Config
from app.core.templates import TemplateManager
from app.models.faiss_index import FAISSIndex
from app.models.schemas import ChatRequest, ChatResponse
from app.models.llm import LLM
from app.models.ocr import OCR

router = APIRouter(redirect_slashes=False)

ocr = OCR()
tm = TemplateManager()
llm = LLM(
    api_key=Config.OPENAI_API_KEY,
    base_url=Config.OPENAI_BASE_URL,
)
faiss = FAISSIndex(
    index_path=Config.FAISS_INDEX_PATH,
    meta_path=Config.METADATA_PATH,
    embed_dim=Config.EMBED_DIM,
    similarity_threshold=Config.SIMILARITY_THRESHOLD,
)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    extra_relevant = None

    # 1. Extract text and if there’s a Base64 image, decode + OCR
    if request.image:
        try:
            ocr_text = ocr.extract_text(request.image)
            query_embedding = await llm.embed(request.question)
            extra_relevant = faiss.search(query_embedding, k=15)

            augmented_query = f"{request.question}\n\nOCR result:\n{ocr_text}"
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"OCR decoding error: {e}")
    else:
        augmented_query = request.question

    if not augmented_query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    # 2. Embed the augmented query
    query_embedding = await llm.embed(augmented_query)

    # 3. Search FAISS
    relevant = faiss.search(query_embedding, k=15)
    if extra_relevant:
        relevant.extend(extra_relevant)

    if not relevant:
        return ChatResponse(
            answer="I'm sorry, I don't have enough context to answer that question.",
            links=[],
        )

    # 4. Collect excerpts and metadata
    excerpts = faiss.generate_excerpts(relevant)

    # 5. Build prompt for OpenAI
    prompt = tm.build_prompt(excerpts, augmented_query)

    # 6. Generate response using OpenAI
    try:
        response = await llm.generate_response(
            prompt, response_format=Config.RESPONSE_FORMAT
        )
        if response.refusal:
            return ChatResponse(
                answer="I'm sorry, I don't have enough context to answer that question.",
                links=[],
            )

        data = json.loads(response.content.strip())
        return ChatResponse(answer=data["answer"], links=data["links"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OpenAI API error: {e}")


def include_router(app):
    app.include_router(router)
