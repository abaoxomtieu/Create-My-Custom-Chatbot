from fastapi import APIRouter, status, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from langchain_core.runnables import RunnableConfig

from src.utils.logger import logger
import json
from src.apis.interfaces.chat_interface import (
    CustomChatbotBody,
)
from src.agents.primary_chatbot.flow import lesson_plan_design_agent
from src.agents.custom_chatbot.flow import custom_chatbot
from langchain_core.messages.ai import AIMessageChunk

router = APIRouter(prefix="/ai", tags=["AI"])


async def message_generator(
    input_graph: dict, background: BackgroundTasks, config: RunnableConfig
):
    try:
        last_output_state = None
        temp = ""

        try:
            async for event in custom_chatbot.astream(
                input=input_graph, stream_mode=["messages", "values"], config=config
            ):
                try:
                    event_type, event_message = event
                    if event_type == "messages":
                        message, _ = event_message
                        if isinstance(message, AIMessageChunk):
                            temp += message.content
                            yield json.dumps(
                                {
                                    "type": "message",
                                    "content": temp,
                                },
                                ensure_ascii=False,
                            )
                    if event_type == "values":
                        last_output_state = event_message
                except Exception as e:
                    logger.error(f"Error processing stream event: {str(e)}")
                    yield json.dumps(
                        {
                            "type": "error",
                            "content": "Error processing response " + str(e),
                        },
                        ensure_ascii=False,
                    )
                    return

            if last_output_state is None:
                raise ValueError("No output state received from workflow")

            try:
                final_response = json.dumps(
                    {
                        "type": "final",
                        "content": {
                            "final_response": last_output_state["messages"][-1].content,
                        },
                    },
                    ensure_ascii=False,
                )
                yield final_response
            except Exception as e:
                logger.error(f"Error processing final response: {str(e)}")
                yield json.dumps(
                    {
                        "type": "error",
                        "content": "Error processing the final response" + str(e),
                    },
                    ensure_ascii=False,
                )
                return

        except Exception as e:
            logger.error(f"Error in workflow stream: {str(e)}")
            yield json.dumps(
                {"type": "error", "content": "Error processing stream" + str(e)},
                ensure_ascii=False,
            )
            return

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        yield json.dumps(
            {"type": "error", "content": "An unexpected error occurred" + str(e)},
            ensure_ascii=False,
        )
        return


@router.post("/custom_chatbot/stream")
async def primary_chat_stream(body: CustomChatbotBody, background: BackgroundTasks):
    try:
        return StreamingResponse(
            message_generator(
                input_graph={
                    "messages": [("user", body.query)],
                },
                config={"configurable": {"thread_id": body.conversation_id}},
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
