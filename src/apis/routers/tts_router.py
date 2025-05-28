from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from transformers import VitsModel, AutoTokenizer
import torch
import os
import uuid
from fastapi.responses import FileResponse
import soundfile as sf
import numpy as np
from src.utils.logger import logger

router = APIRouter()


class TTSRequest(BaseModel):
    text: str


# Initialize model and tokenizer globally
try:
    logger.info("Loading TTS model and tokenizer...")
    model = VitsModel.from_pretrained("facebook/mms-tts-vie")
    tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
    logger.info("TTS model and tokenizer loaded successfully")
except Exception as e:
    logger.error(f"Failed to load TTS model: {str(e)}")
    raise


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    try:
        logger.info(f"Processing TTS request for text: {request.text[:50]}...")

        # Tokenize input
        inputs = tokenizer(request.text, return_tensors="pt")
        logger.info("Text tokenized successfully")

        # Generate audio
        with torch.no_grad():
            output = model(**inputs).waveform
        logger.info("Audio generated successfully")

        # Convert tensor to numpy array
        audio_numpy = output.squeeze().cpu().numpy()

        # Create audio directory if it doesn't exist
        audio_dir = os.path.join(os.getcwd(), "audio_files")
        os.makedirs(audio_dir, exist_ok=True)

        # Generate unique filename
        audio_filename = f"{uuid.uuid4()}.wav"
        audio_path = os.path.join(audio_dir, audio_filename)

        # Save audio file using soundfile
        sf.write(audio_path, audio_numpy, model.config.sampling_rate)
        logger.info(f"Audio saved to {audio_path}")

        # Return audio file
        return FileResponse(audio_path, media_type="audio/wav", filename=audio_filename)
    except Exception as e:
        logger.error(f"Error in text_to_speech: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate speech: {str(e)}"
        )
