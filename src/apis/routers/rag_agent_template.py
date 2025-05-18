from fastapi import APIRouter, status, BackgroundTasks, Query
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from src.utils.logger import logger
from typing import Optional, List, Dict, Any
import json
import datetime
from src.apis.interfaces.chat_interface import (
    PrimaryChatBody,
)
from src.agents.rag_agent_template.flow import rag_agent_template_agent
from langchain_core.messages.ai import AIMessageChunk
from src.config.mongo import bot_crud
from bson import ObjectId

router = APIRouter(prefix="/ai", tags=["AI"])


class RagAgentBody(BaseModel):
    query: dict = Field(..., title="User's query message in role-based format")
    bot_id: Optional[str] = Field(None, title="Bot ID")
    prompt: Optional[str] = Field(None, title="Prompt")
    conversation_id: Optional[str] = Field(None, title="Conversation ID")
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Hình này là ở đâu vậy?"},
                        {
                            "type": "image",
                            "source_type": "url",
                            "url": "https://example.com/image.jpg",
                        },
                    ],
                },
                "bot_id": "1",
                "prompt": "You are a helpful assistant.",
                "conversation_id": "1",
            }
        }
    }


async def message_generator(input_graph: dict, config: dict):
    # try:
    last_output_state = None
    temp = ""

    # try:
    async for event in rag_agent_template_agent.astream(
        input=input_graph,
        stream_mode=["messages", "values"],
        config=config,
    ):
        # try:
        event_type, event_message = event
        if event_type == "messages":
            message, metadata = event_message
            if isinstance(message, AIMessageChunk) and metadata["langgraph_node"] in [
                "generate_answer_rag"
            ]:
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

    if "messages" not in last_output_state:
        raise ValueError("No LLM response in output")

    # try:
    final_response = json.dumps(
        {
            "type": "final",
            "content": {
                "final_response": last_output_state["messages"][-1].content,
                "selected_ids": last_output_state.get("selected_ids", []),
                "selected_documents": last_output_state.get("selected_documents", []),
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
async def rag_agent_template_stream(body: RagAgentBody):
    try:
        tools = []
        input_graph = {"messages": body.query}
        if not body.prompt and body.bot_id:

            data = await bot_crud.find_by_id(body.bot_id)
            if not data:
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"error": "Bot not found"},
                )
            body.prompt = data["prompt"]
            tools = data["tools"]
        if not body.prompt:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": "Prompt is required"},
            )
        input_graph = {"messages": body.query, "prompt": body.prompt, "tools": tools}
        config = {
            "configurable": {
                "thread_id": body.conversation_id if body.conversation_id else "1",
                "bot_id": body.bot_id if body.bot_id else "",
            }
        }

        return StreamingResponse(
            message_generator(
                input_graph=input_graph,
                config=config,
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

    if not body.prompt and body.bot_id:
        data = await bot_crud.find_by_id(body.bot_id)
        if not data:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": "Bot not found"},
            )
        body.prompt = data["prompt"]
    if not body.prompt:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Prompt is required"},
        )

    input_graph = {"messages": body.query, "prompt": body.prompt}

    config = {
        "configurable": {
            "thread_id": body.conversation_id if body.conversation_id else "1",
            "bot_id": body.bot_id if body.bot_id else "not found",
        }
    }

    response = await rag_agent_template_agent.ainvoke(input_graph, config=config)
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "final_response": response["messages"][-1].content,
        },
    )


class ChatbotListResponse(BaseModel):
    chatbots: List[Dict[str, Any]]


class ChatbotDetailResponse(BaseModel):
    id: str
    name: str
    prompt: str
    tools: List[Any] = []
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ChatbotUpdateRequest(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None
    tools: Optional[List[Any]] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Updated Chatbot Name",
                "prompt": "You are a helpful assistant specialized in travel advice.",
                "tools": [],
            }
        }
    }


@router.get("/chatbots", response_model=ChatbotListResponse)
async def list_chatbots():
    """
    List all available chatbots.

    Returns:
        A list of chatbot objects with their details.
    """
    try:
        # Fetch all chatbots from database using read method
        chatbots = await bot_crud.read({})

        # Transform the data to include id instead of _id for consistency
        for bot in chatbots:
            if "_id" in bot:
                bot["id"] = str(bot.pop("_id"))

            # Convert datetime objects to ISO format strings
            if "created_at" in bot and isinstance(bot["created_at"], datetime.datetime):
                bot["created_at"] = bot["created_at"].isoformat()

            if "updated_at" in bot and isinstance(bot["updated_at"], datetime.datetime):
                bot["updated_at"] = bot["updated_at"].isoformat()

            if "expire_at" in bot and isinstance(bot["expire_at"], datetime.datetime):
                bot["expire_at"] = bot["expire_at"].isoformat()

        logger.info(f"Retrieved {len(chatbots)} chatbots")
        return ChatbotListResponse(chatbots=chatbots)

    except Exception as e:
        logger.error(f"Error retrieving chatbots: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Failed to retrieve chatbots: {str(e)}"},
        )


@router.get("/chatbots/{chatbot_id}", response_model=ChatbotDetailResponse)
async def get_chatbot_detail(chatbot_id: str):
    """
    Get detailed information about a specific chatbot.

    Args:
        chatbot_id: The ID of the chatbot to retrieve.

    Returns:
        Detailed information about the requested chatbot.
    """
    try:
        chatbot = await bot_crud.find_by_id(chatbot_id)

        if not chatbot:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": f"Chatbot with ID {chatbot_id} not found"},
            )

        if "_id" in chatbot:
            chatbot["id"] = str(chatbot.pop("_id"))

        # Convert datetime objects to ISO format strings
        if "created_at" in chatbot and isinstance(
            chatbot["created_at"], datetime.datetime
        ):
            chatbot["created_at"] = chatbot["created_at"].isoformat()

        if "updated_at" in chatbot and isinstance(
            chatbot["updated_at"], datetime.datetime
        ):
            chatbot["updated_at"] = chatbot["updated_at"].isoformat()

        if "expire_at" in chatbot and isinstance(
            chatbot["expire_at"], datetime.datetime
        ):
            chatbot["expire_at"] = chatbot["expire_at"].isoformat()

        logger.info(f"Retrieved chatbot details for ID: {chatbot_id}")
        return chatbot

    except Exception as e:
        logger.error(f"Error retrieving chatbot details: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Failed to retrieve chatbots: {str(e)}"},
        )


@router.put("/chatbots/{chatbot_id}", response_model=ChatbotDetailResponse)
async def update_chatbot(chatbot_id: str, update_data: ChatbotUpdateRequest):
    """
    Update a chatbot's properties.

    Args:
        chatbot_id: The ID of the chatbot to update.
        update_data: The data to update the chatbot with.

    Returns:
        The updated chatbot details.
    """
    try:
        # First check if the chatbot exists
        existing_chatbot = await bot_crud.find_by_id(chatbot_id)

        if not existing_chatbot:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": f"Chatbot with ID {chatbot_id} not found"},
            )

        # Prepare update data (only include non-None fields)
        update_fields = {}
        if update_data.name is not None:
            update_fields["name"] = update_data.name
        if update_data.prompt is not None:
            update_fields["prompt"] = update_data.prompt
        if update_data.tools is not None:
            update_fields["tools"] = update_data.tools

        # Add updated_at timestamp
        update_fields["updated_at"] = datetime.datetime.now()

        # Update the chatbot
        updated = await bot_crud.update({"_id": ObjectId(chatbot_id)}, update_fields)

        if not updated:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Failed to update chatbot"},
            )

        # Get the updated chatbot
        updated_chatbot = await bot_crud.find_by_id(chatbot_id)

        # Transform _id to id for consistency
        if "_id" in updated_chatbot:
            updated_chatbot["id"] = str(updated_chatbot.pop("_id"))

        # Convert datetime objects to ISO format strings
        if "created_at" in updated_chatbot and isinstance(
            updated_chatbot["created_at"], datetime.datetime
        ):
            updated_chatbot["created_at"] = updated_chatbot["created_at"].isoformat()

        if "updated_at" in updated_chatbot and isinstance(
            updated_chatbot["updated_at"], datetime.datetime
        ):
            updated_chatbot["updated_at"] = updated_chatbot["updated_at"].isoformat()

        if "expire_at" in updated_chatbot and isinstance(
            updated_chatbot["expire_at"], datetime.datetime
        ):
            updated_chatbot["expire_at"] = updated_chatbot["expire_at"].isoformat()

        logger.info(f"Updated chatbot with ID: {chatbot_id}")
        return updated_chatbot

    except Exception as e:
        logger.error(f"Error updating chatbot: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Failed to update chatbot: {str(e)}"},
        )
