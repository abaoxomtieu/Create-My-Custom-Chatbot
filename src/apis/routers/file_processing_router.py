from fastapi import APIRouter, status, UploadFile, File, Form, Depends
from fastapi.responses import JSONResponse
from src.utils.logger import logger
from src.apis.interfaces.file_processing_interface import (
    FileProcessingBody,
    FileAnalysisResponse,
    FileIngressResponse,
)
from src.data_preprocessing.preprocessing import (
    extract_and_chunk_documents,
    process_and_index_file,
)
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
    """
    Analyze a file and return information about its content (word count and image count).
    """
    try:
        logger.info(f"Analyzing file: {file.filename} for bot: {body.bot_id}")

        # Create a temporary file
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)

        # Save the uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Get file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        file_type = file_extension.replace(".", "").upper()

        word_count = 0
        image_count = 0

        # Process based on file type
        if file_extension == ".pdf":
            # Count words and images in PDF
            doc = fitz.open(temp_file_path)

            for page in doc:
                text = page.get_text("text")
                word_count += len(text.split())
                image_count += len(page.get_images(full=True))

        elif file_extension == ".docx":
            # Count words and images in DOCX
            doc = DocxDoc(temp_file_path)

            # Count words
            for para in doc.paragraphs:
                word_count += len(para.text.split())

            # Count images
            image_count = 0
            for rel in doc.part._rels.values():
                if "image" in rel.target_ref:
                    image_count += 1
        else:
            # Clean up temporary file
            shutil.rmtree(temp_dir)
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"error": f"Unsupported file type: {file_extension}"},
            )

        # Clean up temporary file
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
    """
    Process and index a file with fixed chunk size (1000) and overlap (200).
    """
    try:
        logger.info(
            f"Processing and indexing file: {file.filename} for bot: {body.bot_id}"
        )

        # Create a temporary file
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)

        # Save the uploaded file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Fixed chunk size and overlap as per requirements
        chunk_size = 1000
        chunk_overlap = 200

        # Process the file
        documents = process_and_index_file(
            file_path=temp_file_path, 
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap,
            batch_size=30,
            bot_id=body.bot_id
        )

        # bot_id is already added to document metadata in process_and_index_file

        # Add documents to vector store
        test_rag_vector_store.add_documents(documents)

        # Add retrieve_document tool to the chatbot if it doesn't exist
        try:
            # Get the current chatbot
            chatbot = await bot_crud.find_by_id(body.bot_id)

            if chatbot:
                # Check if tools field exists and if retrieve_document is already in tools
                tools = chatbot.get("tools", [])

                # Check if retrieve_document tool already exists
                retrieve_document_exists = False
                for tool in tools:
                    if (
                        isinstance(tool, dict)
                        and tool.get("name") == "retrieve_document"
                    ):
                        retrieve_document_exists = True
                        break

                # If retrieve_document tool doesn't exist, add it
                if not retrieve_document_exists:
                    tools.append("retrieve_document")

                    # Update the chatbot with the new tools
                    await bot_crud.update(
                        {"_id": ObjectId(body.bot_id)}, {"tools": tools}
                    )
                    logger.info(
                        f"Added retrieve_document tool to chatbot {body.bot_id}"
                    )
        except Exception as e:
            logger.error(f"Error updating chatbot tools: {str(e)}")
            # Continue with the process even if updating tools fails

        # Clean up temporary file
        shutil.rmtree(temp_dir)

        # Return response with chunk count
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
