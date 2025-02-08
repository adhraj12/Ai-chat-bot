// App.js
import React, { useState, useRef } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [bot, setBot] = useState("banker"); // "banker" or "actor"
  const [conversation, setConversation] = useState([]); // Array of message objects
  const [input, setInput] = useState("");
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Send text message to the backend chat endpoint.
  const sendMessage = async () => {
    if (input.trim() === "") return;
    const userMessage = { role: "user", content: input };
    setConversation((prev) => [...prev, userMessage]);

    try {
      const response = await axios.post("http://localhost:8000/chat", {
        message: input,
        conversation: conversation, // sending the conversation history
        bot: bot,
      });
      if (response.data.reply) {
        const botMessage = { role: "assistant", content: response.data.reply };
        setConversation((prev) => [...prev, botMessage]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
    }
    setInput("");
  };

  // Start recording audio
  const startRecording = async () => {
    setRecording(true);
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunksRef.current.push(e.data);
        }
      };
      mediaRecorderRef.current.onstop = handleRecordingStop;
      mediaRecorderRef.current.start();
    } else {
      alert("Audio recording is not supported in this browser.");
    }
  };

  // Stop recording audio
  const stopRecording = () => {
    setRecording(false);
    mediaRecorderRef.current.stop();
  };

  // When recording stops, send the audio to the /whisper endpoint.
  const handleRecordingStop = async () => {
    const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
    const formData = new FormData();
    formData.append("file", audioBlob, "recording.wav");
    try {
      const response = await axios.post("http://localhost:8000/whisper", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      if (response.data.transcript) {
        setInput(response.data.transcript);
      }
    } catch (error) {
      console.error("Error transcribing audio:", error);
    }
  };

  // Play the bot's reply using text-to-speech.
  const playAudio = async (text) => {
    try {
      const response = await axios.post("http://localhost:8000/tts", null, {
        params: {
          text: text,
          language_code: "en-US", // you can adjust this based on the language
        },
        responseType: "blob",
      });
      const audioUrl = URL.createObjectURL(response.data);
      const audio = new Audio(audioUrl);
      audio.play();
    } catch (error) {
      console.error("Error generating TTS:", error);
    }
  };

  return (
    <div className="App">
      <div className="sidebar">
        {/* Replace with your actual logo image */}
        <img src="/logo.png" alt="Hackathon Logo" className="logo" />
        <div className="team-members">
          <p>Adhiraj Jagtap</p>
          <p>Indra Kale</p>
          <p>Parth Takate</p>
        </div>
      </div>
      <div className="chat-container">
        <div className="bot-selector">
          <label>Select Bot: </label>
          <select
            value={bot}
            onChange={(e) => {
              setBot(e.target.value);
              // Reset conversation when switching bots.
              setConversation([]);
            }}
          >
            <option value="banker">Rude Banker</option>
            <option value="actor">Humble Actor</option>
          </select>
        </div>
        <div className="chat-window">
          {conversation.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <p>{msg.content}</p>
              {msg.role === "assistant" && (
                <button onClick={() => playAudio(msg.content)}>🔊</button>
              )}
            </div>
          ))}
        </div>
        <div className="input-area">
          <input
            type="text"
            value={input}
            placeholder="Type your message here..."
            onChange={(e) => setInput(e.target.value)}
          />
          <button onClick={sendMessage}>Send</button>
          {!recording ? (
            <button onClick={startRecording}>🎤</button>
          ) : (
            <button onClick={stopRecording}>⏹️</button>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
