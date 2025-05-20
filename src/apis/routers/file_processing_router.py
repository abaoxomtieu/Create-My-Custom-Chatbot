from fastapi import APIRouter, status, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from src.utils.logger import logger
from src.apis.interfaces.file_processing_interface import (
    FileProcessingBody,
    FileAnalysisResponse,
    FileIngressResponse,
)
from src.data_preprocessing.preprocessing import process_and_index_file
import os
import tempfile
import shutil
from PIL import Image
import fitz  # PyMuPDF
from docx import Document as DocxDoc
from src.config.vector_store import test_rag_vector_store
from src.config.mongo import bot_crud
from bson import ObjectId

router = APIRouter(prefix="/file", tags=["File Processing"])


async def get_file_processing_body(bot_id: str = Form(...)):
    return FileProcessingBody(bot_id=bot_id)


@router.post("/analyze", response_model=FileAnalysisResponse)
async def analyze_file(
    file: UploadFile = File(...),
    body: FileProcessingBody = Depends(get_file_processing_body),
):

    try:
        logger.info(f"Analyzing file: {file.filename} for bot: {body.bot_id}")
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_extension = os.path.splitext(file.filename)[1].lower()
        file_type = file_extension.replace(".", "").upper()
        word_count = 0
        image_count = 0
        if file_extension == ".pdf":
            doc = fitz.open(temp_file_path)
            for page in doc:
                text = page.get_text("text")
                word_count += len(text.split())
                image_count += len(page.get_images(full=True))
        elif file_extension == ".docx":
            doc = DocxDoc(temp_file_path)
            for para in doc.paragraphs:
                word_count += len(para.text.split())
            image_count = 0
            for rel in doc.part._rels.values():
                if "image" in rel.target_ref:
                    image_count += 1
        else:
            shutil.rmtree(temp_dir)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"Unsupported file type: {file_extension}"},
            )

        shutil.rmtree(temp_dir)

        return FileAnalysisResponse(
            bot_id=body.bot_id,
            file_path=file.filename,
            word_count=word_count,
            image_count=image_count,
            file_type=file_type,
        )

    except Exception as e:
        logger.error(f"Error analyzing file: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": f"Error analyzing file: {str(e)}"},
        )


@router.post("/ingress", response_model=FileIngressResponse)
async def ingress_file(
    file: UploadFile = File(...),
    body: FileProcessingBody = Depends(get_file_processing_body),
):
    try:
        logger.info(
            f"Processing and indexing file: {file.filename} for bot: {body.bot_id}"
        )

        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)

        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        chunk_size = 1000
        chunk_overlap = 200
        documents = process_and_index_file(
            file_path=temp_file_path,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            batch_size=30,
            bot_id=body.bot_id,
        )

        test_rag_vector_store.add_documents(documents)
        try:
            chatbot = await bot_crud.find_by_id(body.bot_id)
            if chatbot:
                tools = chatbot.get("tools", [])
                retrieve_document_exists = False
                for tool in tools:
                    if (
                        isinstance(tool, dict)
                        and tool.get("name") == "retrieve_document"
                    ):
                        retrieve_document_exists = True
                        break
                if not retrieve_document_exists:
                    tools.append("retrieve_document")
                    await bot_crud.update(
                        {"_id": ObjectId(body.bot_id)}, {"tools": tools}
                    )
                    logger.info(
                        f"Added retrieve_document tool to chatbot {body.bot_id}"
                    )
        except Exception as e:
            logger.error(f"Error updating chatbot tools: {str(e)}")
        shutil.rmtree(temp_dir)
        chunks_count = len(documents)

        return FileIngressResponse(
            bot_id=body.bot_id,
            file_path=file.filename,
            chunks_count=chunks_count,
            success=True,
            message=f"File processed and indexed successfully. Created {chunks_count} chunks.",
        )

    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "bot_id": body.bot_id,
                "file_path": file.filename if file else "unknown",
                "chunks_count": 0,
                "success": False,
                "message": f"Error processing file: {str(e)}",
            },
        )
