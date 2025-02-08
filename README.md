# AI Bot with Advance Assistant Features

An interactive AI-powered chatbot with voice capabilities that listens to user queries and responds in the same language. Choose between two unique bot personas—a **Rude Banker** and a **Humble Actor**—each with its own distinct personality and backstory. This project demonstrates how to integrate Speech-to-Text (using OpenAI's Whisper API), Natural Language Processing (using OpenAI's Chat API), and Text-to-Speech (using Google Cloud Text-to-Speech API) into one complete application.

## Features

- **Dual Bot Personas:**  
  - **Rude Banker:** A sarcastic and dismissive banker who only answers banking-related queries.
  - **Humble Actor:** A kind and thoughtful actor who shares personal experiences and offers life advice.
- **Multilingual Support:**  
  Bots detect the language of the user's input and reply in the same language.
- **Voice Input & Output:**  
  - **Speech-to-Text:** Convert spoken queries into text using the Whisper API.
  - **Text-to-Speech:** Convert bot responses into audio using Google Cloud Text-to-Speech.
- **Web-Based Chat Interface:**  
  A modern, responsive UI built with React that mimics the look and feel of popular chat applications.
- **Session Memory:**  
  Conversation history is maintained during a session for context-aware responses.
- **Customizable Avatars and Team Info:**  
  A sidebar displays a hackathon logo and team member names, adding a personal touch to the app.

## Tech Stack

- **Frontend:**  
  - React
  - JavaScript / JSX
  - Tailwind CSS (or similar CSS for styling)
  - Axios for API requests
- **Backend:**  
  - Python
  - FastAPI for building the REST API
  - Uvicorn for running the FastAPI server
  - OpenAI API (Chat & Whisper)
  - Google Cloud Text-to-Speech API


## Setup & Installation

### Prerequisites

- **Backend:**
  - Python 3.8+
  - API keys for [OpenAI](https://openai.com/) and [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech)
- **Frontend:**
  - Node.js and npm

### Backend Setup

1. Navigate to the backend folder:
   ```bash
   cd ai-bot-voice-assistant/backend

2. Install the dependencies:
```bash
    pip install -r requirements.txt
```
3. Start the FastAPI server:
```bash
uvicorn main:app --reload
```
The backend will be available at http://localhost:8000

### Frontend Setup
1. Navigate to the frontend folder:
```bash
cd ai-bot-voice-assistant/frontend
```
2. Install the dependencies:
```bash
npm install
```
3. Start the React development server:
```bash
npm start
```
Your browser will open the app at http://localhost:3000.

## Usage
1. **Choose a Bot Persona:**
Use the dropdown menu to switch between the Rude Banker and the Humble Actor. Changing the persona will reset the current conversation.

2. **Chatting:**
 - Text Input: Type your query into the chat box and click Send.
 - Voice Input: Click the microphone button (🎤) to record your query. Click the stop button (⏹️) when finished, and the recorded audio will be transcribed to text.
   
3. **Voice Response:**
When a bot response appears, click the speaker button (🔊) next to the message to hear it spoken aloud.
