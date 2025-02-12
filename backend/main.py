# main.py
import os
import tempfile
import io
import base64
import requests
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import openai

GEMINI_API_KEY = "AIzaSyC_NnTR_S_wudHeAapqPhMHXfujilQX0wI"
GOOGLE_TTS_API_KEY = "AIzaSyABY-tZxHZYkyXB3OJxhH2_sm_4m9xKOwY"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class ChatRequest(BaseModel):
    message: str
    conversation: Optional[List[dict]] = []
    bot: str

def detect_language(text: str) -> str:
    for char in text:
        if "\u0900" <= char <= "\u097F":
            return "hi-IN"
    return "en-US"

def call_gemini(messages: List[dict]) -> str:
    url = "https://gemini.googleapis.com/v2/flash"
    payload = {
        "model": "gemini-2.0-flash",
        "messages": messages,
        "temperature": 0.7
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GEMINI_API_KEY}"
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    print("Gemini API response:", data)
    return data["choices"][0]["message"]["content"]

class ChatBotMemory:
    def __init__(self, max_tokens=1000):
        self.max_tokens = max_tokens
        self.short_term_memory = []
        self.long_term_memory = []

    def add_message(self, role, message):
        self.short_term_memory.append({"role": role, "message": message})
        self.compress_memory()

    def compress_memory(self):
        current_tokens = sum(len(msg["message"]) for msg in self.short_term_memory)
        while current_tokens > self.max_tokens:
            if not self.short_term_memory:
                break
            oldest_msg = self.short_term_memory.pop(0)
            summary = self.summarize(oldest_msg["message"])
            self.long_term_memory.append(summary)
            current_tokens = sum(len(msg["message"]) for msg in self.short_term_memory)

    def summarize(self, message):
        return f"Summary: {message[:20]}..."

    def get_context(self):
        stm_context = " ".join(msg["message"] for msg in self.short_term_memory)
        ltm_context = " ".join(self.long_term_memory)
        return f"{ltm_context} {stm_context}".strip()

memory = ChatBotMemory(max_tokens=1500)

@app.post("/chat")
async def chat(req: ChatRequest):
    bot = req.bot.lower()
    language_code = detect_language(req.message)
    system_prompt = SYSTEM_PROMPTS.get(bot, SYSTEM_PROMPTS["banker"])

    if language_code == "hi-IN":
        system_prompt += "\nकृपया हिंदी में उत्तर दें।"
    else:
        system_prompt += "\nPlease reply in English."

    memory.add_message("user", req.message)
    context = memory.get_context()

    messages = [{"role": "system", "content": system_prompt}]
    conversation_history = []
    for msg_dict in memory.short_term_memory:
        if msg_dict["role"] != "user" and msg_dict["role"] != "assistant":
            continue
        conversation_history.append({"role": msg_dict["role"], "content": msg_dict["message"]})
    if conversation_history:
        messages.extend(conversation_history)

    try:
        bot_reply_message = call_gemini(messages)
        memory.add_message("assistant", bot_reply_message)
        return {"reply": bot_reply_message}
    except Exception as e:
        return {"error": str(e)}

@app.post("/whisper")
async def transcribe_audio(file: UploadFile = File(...)):
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

@app.post("/tts")
async def text_to_speech(text: str, language_code: str = "en-US"):
    try:
        url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={GOOGLE_TTS_API_KEY}"
        payload = {
            "input": {"text": text},
            "voice": {"languageCode": language_code, "ssmlGender": "NEUTRAL"},
            "audioConfig": {"audioEncoding": "MP3"}
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        audio_content = data.get("audioContent")
        if not audio_content:
            raise Exception("No audio content received from TTS API")
        audio_bytes = base64.b64decode(audio_content)
        return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")
    except Exception as e:
        return {"error": str(e)}
