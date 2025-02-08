# main.py
import os
import tempfile
import io
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import openai

# Set your OpenAI API key as an environment variable.
# For example, in your terminal (replace <your-key> with your key):
# export OPENAI_API_KEY=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

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

# Allow CORS so that the React frontend (likely on another port) can communicate.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# System prompts for our two bots.
SYSTEM_PROMPTS = {
    "banker": (
        "You are Mr. Fendleton, a rude banker who has been working at the bank for far too long. "
        "You find most customers to be a nuisance and their questions tedious. You answer with disdain, "
        "sarcasm, and reluctance, and you only address questions related to banking. If a question is not banking‑related, "
        "respond dismissively."
    ),
    "actor": (
        "You are Keanu Reeves, a humble actor known for your kindness and humility. "
        "You always credit your luck and your team, avoid boasting, and offer thoughtful, supportive advice. "
        "You only address questions related to acting, personal experiences, or general life advice; if the conversation drifts, "
        "politely steer it back."
    )
}


# Pydantic model for chat requests.
class ChatRequest(BaseModel):
    message: str
    conversation: Optional[List[dict]] = []  # conversation history; each message has a 'role' and 'content'
    bot: str  # "banker" or "actor"


@app.post("/chat")
async def chat(req: ChatRequest):
    bot = req.bot.lower()
    system_prompt = SYSTEM_PROMPTS.get(bot, SYSTEM_PROMPTS["banker"])
    
    # Build the message list to send to the OpenAI API.
    messages = [{"role": "system", "content": system_prompt}]
    if req.conversation:
        messages.extend(req.conversation)
    messages.append({"role": "user", "content": req.message})
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or any model you prefer
            messages=messages,
            temperature=0.7
        )
        bot_reply = response.choices[0].message.content
        return {"reply": bot_reply}
    except Exception as e:
        return {"error": str(e)}


@app.post("/whisper")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Accepts an audio file upload and returns its transcription using OpenAI's Whisper API.
    """
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        with open(tmp_path, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
        os.remove(tmp_path)
        return {"transcript": transcript["text"]}
    except Exception as e:
        return {"error": str(e)}


# For text-to-speech, we use Google Cloud Text-to-Speech.
# Make sure you have set the environment variable GOOGLE_APPLICATION_CREDENTIALS
# pointing to your service account key JSON file.
from google.cloud import texttospeech

@app.post("/tts")
async def text_to_speech(text: str, language_code: str = "en-US"):
    """
    Converts provided text to speech and returns an MP3 audio stream.
    """
    try:
        client = texttospeech.TextToSpeechClient()

        synthesis_input = texttospeech.SynthesisInput(text=text)
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        return StreamingResponse(io.BytesIO(response.audio_content), media_type="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}
