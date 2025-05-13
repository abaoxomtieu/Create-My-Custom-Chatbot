from fastapi import APIRouter, status, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from src.utils.logger import logger
from typing import Optional
import json
from src.apis.interfaces.chat_interface import (
    PrimaryChatBody,
)
from src.agents.rag_agent_template.flow import rag_agent_template_agent
from langchain_core.messages.ai import AIMessageChunk

router = APIRouter(prefix="/ai", tags=["AI"])


class RagAgentBody(BaseModel):
    query: dict = Field(..., title="User's query message in role-based format")
    history: Optional[list] = Field(None, title="Chat history in role-based format")
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Hình này là ở đâu vậy?"},
                        {"type": "image", "source_type": "url", "url": "https://example.com/image.jpg"}
                    ]
                },
                "history": [
                    {"role": "user", "content": "Bạn là ai vậy"},
                    {"role": "assistant", "content": "Tôi là chuyên gia du lịch"}
                ]
            }
        }
    }


async def message_generator(input_graph: dict, background: BackgroundTasks):
    # try:
        last_output_state = None
        temp = ""

        # try:
        async for event in rag_agent_template_agent.astream(
            input=input_graph,
            stream_mode=["messages", "values"],
        ):
            # try:
            event_type, event_message = event
            if event_type == "messages":
                message, metadata = event_message
                print("message", message)
                if isinstance(message, AIMessageChunk) and metadata[
                    "langgraph_node"
                ] in ["generate_answer_rag"]:
                    temp += message.content
                    yield json.dumps(
                        {
                            "type": "message",
                            "content": temp,
                        },
                        ensure_ascii=False,
                    ) + "\n\n"
            if event_type == "values":
                last_output_state = event_message
            # except Exception as e:
            #     logger.error(f"Error processing stream event: {str(e)}")
            #     yield json.dumps(
            #         {
            #             "type": "error",
            #             "content": "Error processing response " + str(e),
            #         },
            #         ensure_ascii=False,
            #     ) + "\n\n"
            #     return

        if last_output_state is None:
            raise ValueError("No output state received from workflow")

        if "llm_response" not in last_output_state:
            raise ValueError("No LLM response in output")

        # try:
        final_response = json.dumps(
            {
                "type": "final",
                "content": {
                    "final_response": last_output_state["llm_response"],
                    "selected_ids": last_output_state.get("selected_ids", []),
                    "selected_documents": last_output_state.get(
                        "selected_documents", []
                    ),
                },
            },
            ensure_ascii=False,
        )
        yield final_response + "\n\n"
        # except Exception as e:
        #     logger.error(f"Error processing final response: {str(e)}")
        #     yield json.dumps(
        #         {
        #             "type": "error",
        #             "content": "Error processing the final response: " + str(e),
        #         },
        #         ensure_ascii=False,
        #     ) + "\n\n"
        #     return

        # except Exception as e:
        #     logger.error(f"Error in workflow stream: {str(e)}")
        #     yield json.dumps(
        #         {"type": "error", "content": "Error processing stream: " + str(e)},
        #         ensure_ascii=False,
        #     ) + "\n\n"
        #     return

    # except Exception as e:
    #     logger.error(f"Unexpected error: {str(e)}")
    #     yield json.dumps(
    #         {"type": "error", "content": "An unexpected error occurred: " + str(e)},
    #         ensure_ascii=False,
    #     ) + "\n\n"
    #     return


@router.post("/rag_agent_template/stream")
async def rag_agent_template_stream(body: RagAgentBody, background: BackgroundTasks):
    try:
        input_graph = {
            "messages_history": body.history,
            "messages": body.query
        }

        return StreamingResponse(
            message_generator(
                input_graph=input_graph,
                background=background,
            ),
            media_type="text/event-stream",
        )
    except Exception as e:
        logger.error(f"Error in streaming endpoint: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Streaming error: {str(e)}"},
        )


@router.post("/rag_agent_template")
async def rag_agent_template(body: RagAgentBody):
    logger.info(f"Primary chat request: {body}")

    input_graph = {
        "messages_history": body.history,
        "messages": body.query
    }

    response = await rag_agent_template_agent.ainvoke(input_graph)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "final_response": response["llm_response"],
            "selected_ids": response["selected_ids"],
            "selected_documents": response["selected_documents"],
        },
    )
