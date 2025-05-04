from fastapi import APIRouter, status, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from src.utils.logger import logger
import json
from src.apis.interfaces.chat_interface import (
    PrimaryChatBody,
)
from src.agents.primary_chatbot.flow import lesson_plan_design_agent
from src.agents.prompt_engineer_assistant.flow import prompt_engineer_assistant_agent
from langchain_core.messages.ai import AIMessageChunk

router = APIRouter(prefix="/ai", tags=["AI"])


async def message_generator(input_graph: dict, background: BackgroundTasks):
    try:
        last_output_state = None
        temp = ""

        try:
            async for event in lesson_plan_design_agent.astream(
                input=input_graph,
                stream_mode=["messages", "values"],
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
                            ) + "\n\n"
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
                    ) + "\n\n"
                    return

            if last_output_state is None:
                raise ValueError("No output state received from workflow")

            if "final_response" not in last_output_state:
                raise ValueError("No final response in output")

            try:
                final_response = json.dumps(
                    {
                        "type": "final",
                        "content": {
                            "final_response": last_output_state["final_response"],
                            "lesson_name": str(last_output_state.get("lesson_name")),
                            "subject_name": str(last_output_state.get("subject_name")),
                            "class_number": str(last_output_state.get("class_number")),
                        },
                    },
                    ensure_ascii=False,
                )
                yield final_response + "\n\n"
            except Exception as e:
                logger.error(f"Error processing final response: {str(e)}")
                yield json.dumps(
                    {
                        "type": "error",
                        "content": "Error processing the final response" + str(e),
                    },
                    ensure_ascii=False,
                ) + "\n\n"
                return

        except Exception as e:
            logger.error(f"Error in workflow stream: {str(e)}")
            yield json.dumps(
                {"type": "error", "content": "Error processing stream" + str(e)},
                ensure_ascii=False,
            ) + "\n\n"
            return

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        yield json.dumps(
            {"type": "error", "content": "An unexpected error occurred" + str(e)},
            ensure_ascii=False,
        ) + "\n\n"
        return


@router.post("/primary_chat/stream")
async def primary_chat_stream(body: PrimaryChatBody, background: BackgroundTasks):
    try:
        return StreamingResponse(
            message_generator(
                input_graph={
                    "user_query": body.query,
                    "messages_history": body.history,
                    "lesson_name": body.lesson_name,
                    "subject_name": body.subject_name,
                    "class_number": body.class_number,
                    "entry_response": None,
                    "build_lesson_plan_response": None,
                    "final_response": None,
                    "messages": [("user", body.query)],
                },
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


@router.post("/primary_chat")
async def primary_chat(body: PrimaryChatBody):
    logger.info(f"Primary chat request: {body}")
    response = await lesson_plan_design_agent.ainvoke(
        {
            "user_query": body.query,
            "messages_history": body.history,
            "lesson_name": body.lesson_name,
            "subject_name": body.subject_name,
            "class_number": body.class_number,
            "entry_response": None,
            "build_lesson_plan_response": None,
            "final_response": None,
            "messages": [("user", body.query)],
        }
    )
    final_response = response["final_response"]
    lesson_name = response["lesson_name"]
    subject_name = response["subject_name"]
    class_number = response["class_number"]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "final_response": final_response,
            "lesson_name": str(lesson_name),
            "subject_name": str(subject_name),
            "class_number": str(class_number),
        },
    )


async def prompt_engineer_message_generator(
    input_graph: dict, background: BackgroundTasks
):
    try:
        last_output_state = None
        temp = ""

        try:
            async for event in prompt_engineer_assistant_agent.astream(
                input=input_graph,
                stream_mode=["messages", "values"],
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
                            ) + "\n\n"
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
                    ) + "\n\n"
                    return

            if last_output_state is None:
                raise ValueError("No output state received from workflow")

            if "final_response" not in last_output_state:
                raise ValueError("No final response in output")

            try:
                final_response = (
                    json.dumps(
                        {
                            "type": "final",
                            "content": {
                                "final_response": last_output_state["final_response"],
                            },
                        },
                        ensure_ascii=False,
                    )
                    + "\n\n"
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
                ) + "\n\n"
                return

        except Exception as e:
            logger.error(f"Error in workflow stream: {str(e)}")
            yield json.dumps(
                {"type": "error", "content": "Error processing stream" + str(e)},
                ensure_ascii=False,
            ) + "\n\n"
            return

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        yield json.dumps(
            {"type": "error", "content": "An unexpected error occurred" + str(e)},
            ensure_ascii=False,
        ) + "\n\n"
        return


@router.post("/prompt_engineer/stream")
async def prompt_engineer_stream(body: PrimaryChatBody, background: BackgroundTasks):
    try:
        return StreamingResponse(
            prompt_engineer_message_generator(
                input_graph={
                    "user_query": body.query,
                    "messages_history": body.history,
                    "final_response": None,
                    "messages": [("user", body.query)],
                },
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


@router.post("/prompt_engineer")
async def prompt_engineer(body: PrimaryChatBody):
    logger.info(f"Prompt engineer request: {body}")
    response = await prompt_engineer_assistant_agent.ainvoke(
        {
            "user_query": body.query,
            "messages_history": body.history,
            "final_response": None,
            "messages": [("user", body.query)],
        }
    )
    final_response = response["final_response"]
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "final_response": final_response,
        },
    )
