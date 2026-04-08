import React, { useState, useRef } from "react";
import { AnimatePresence } from "framer-motion";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import LandingPage from "./LandingPage";
import ForkLens from "./ForkLens";

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const SAMPLE_SUGGESTIONS = [
  "I feel lost after finishing my degree",
  "I've spent 15 years in a career that no longer feels like mine",
  "My closest friendship just ended without warning",
];

export default function App() {
  const [input, setInput] = useState("");
  const [started, setStarted] = useState(false);
  const [currentEmotion, setCurrentEmotion] = useState(null);
  
  const inputRef = useRef(null);

  const handleSend = (text) => {
    // We transition to the chat session. 
    // ForkLens manages the actual conversation flow.
    setStarted(true);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-[#0A0E14] flex flex-col text-[#f0ead8] relative antialiased overflow-hidden selection:bg-[#C8A84B] selection:text-[#0A0E14]">
      {/* Global Atmospheric Layers */}
      <div className="constellation" />
      <div className="glow-threshold" />
      <div className="noise-overlay" />
      
      <div className="flex-1 overflow-y-auto custom-scrollbar relative">
        <AnimatePresence mode="wait">
          {!started ? (
            <LandingPage 
              key="landing"
              input={input}
              setInput={setInput}
              handleSend={handleSend}
              handleKeyDown={handleKeyDown}
              inputRef={inputRef}
              SAMPLE_SUGGESTIONS={SAMPLE_SUGGESTIONS}
              setStarted={setStarted}
              currentEmotion={currentEmotion}
            />
          ) : (
            <ForkLens 
              key="chat"
              onReset={() => setStarted(false)} 
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
