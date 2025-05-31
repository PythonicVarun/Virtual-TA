from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import router as api_router

app = FastAPI(
    title="Virtual TA API",
    version=__version__,
    description="A virtual teaching assistant API that integrates OCR, FAISS, and OpenAI for enhanced educational support.",
    openapi_tags=[
        {
            "name": "API",
            "description": "Endpoints for interacting with the Virtual TA API.",
        },
    ],
)
app.router.redirect_slashes = False


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    pass


@app.on_event("shutdown")
async def shutdown_event():
    pass


@app.middleware("http")
async def strip_trailing_slash(request: Request, call_next):
    scope = request.scope
    path = scope["path"]
    if path != "/" and path.endswith("/"):
        scope["path"] = path[:-1]
    return await call_next(request)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def get_application_root_ui():
    html_content = """
    <html>
        <head>
            <title>Virtual TA Chatbot</title>
            <style>
                body { font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: auto; color: #333; display: flex; align-items: center; justify-content: center; }
                h1 { color: #0056b3; }
                p { margin-bottom: 10px; }
                code { background-color: #f4f4f4; padding: 2px 5px; border-radius: 3px; }
                .container { padding: 20px; border: 1px solid #ddd; border-radius: 5px; background-color: #f9f9f9;}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Welcome to the Virtual TA Chatbot</h1>
                <p>This application provides access to the Virtual TA chatbot API.</p>
                <p>
                    To interact with the chatbot, you need to send a <code>POST</code> request to the
                    <code>/api</code> endpoint. The request should be a JSON object containing your question
                    and optionally an image for analysis.
                </p>
                <p>
                    For example, using <code>curl</code>:
                </p>
                <pre><code>curl -X POST -H "Content-Type: application/json" -d '{
    "question": "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
    "image": "'"$(curl -s "https://tds.s-anand.net/images/project-tds-virtual-ta-q1.webp" | base64 -w0)"'"
}' https://virtual-ta.pythonicvarun.me/api</code></pre>
                <p>
                    You can also explore the <a href="/docs">API documentation</a> and <a href="https://github.com/PythonicVarun/Virtual-TA" target="_blank">Source Code</a>.
                </p>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


app.include_router(api_router, prefix="/api", tags=["API"])
