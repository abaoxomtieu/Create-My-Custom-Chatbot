from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from src.apis.routers.chat_router import router as router_chat
from src.apis.routers.adaptive_chat_router import router as router_adaptive_chat
from src.apis.routers.rag_agent_template import router as router_rag_agent_template
from src.apis.routers.file_processing_router import router as router_file_processing
from src.apis.routers.custom_chatbot_router import router as custom_chatbot_processing
# from src.apis.routers.image_explainer_router import router as router_image_explainer

api_router = APIRouter()
api_router.include_router(router_chat)
api_router.include_router(router_adaptive_chat)
api_router.include_router(router_rag_agent_template)
api_router.include_router(router_file_processing)
api_router.include_router(custom_chatbot_processing)
# api_router.include_router(router_image_explainer)


def create_app():
    app = FastAPI(
        docs_url="/",
        title="AI Service",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
