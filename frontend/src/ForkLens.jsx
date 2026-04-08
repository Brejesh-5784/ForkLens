import { useState, useRef, useEffect } from "react";
import axios from "axios";

const API_BASE = "http://localhost:8000";

const WELCOME_MESSAGE = {
  id: "welcome",
  role: "assistant",
  content:
    "Welcome, dear soul. Whatever you're carrying right now — a quiet ache, a impossible choice, a feeling you cannot name — you don't have to carry it alone. Generations of characters have walked this road before you. Share what's on your heart, and together we'll find the one who understands.",
};

export default function ForkLens({ onReset }) {
  const [messages, setMessages] = useState([WELCOME_MESSAGE]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [conversationEnded, setConversationEnded] = useState(false);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    const timeout = setTimeout(() => {
      bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
    }, 100);
    return () => clearTimeout(timeout);
  }, [messages, isTyping]);

  const handleSend = async (text) => {
    const userText = text || input.trim();
    if (!userText || conversationEnded) return;

    setInput("");
    if (inputRef.current) inputRef.current.style.height = 'auto';

    const userMsg = { id: Date.now(), role: "user", content: userText };
    setMessages((prev) => [...prev, userMsg]);
    setIsTyping(true);

    try {
      const response = await axios.post(`${API_BASE}/api/chat`, {
        user_input: userText,
        history: messages.map(m => ({ role: m.role, content: m.content }))
      }, { timeout: 35000 });

      const { text: botText, emotion, score, passages } = response.data;

      const botMsg = {
        id: Date.now() + 1,
        role: "assistant",
        content: botText,
        emotion,
        score,
        passages
      };

      setIsTyping(false);
      setMessages((prev) => [...prev, botMsg]);
    } catch (err) {
      console.error("API Error:", err);
      setIsTyping(false);
      setMessages((prev) => [...prev, {
        id: Date.now() + 1,
        role: "assistant",
        content: "The ink has run dry for a moment... (Connection Error)"
      }]);
    }

    setTimeout(() => inputRef.current?.focus(), 100);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{
        background: "#0A0E14",
        fontFamily: "'EB Garamond', 'Georgia', serif",
      }}
    >
      {/* Top nav */}
      <nav
        className="flex items-center justify-between px-10 h-24 border-b border-white/5 bg-[#0A0E14]/60 backdrop-blur-3xl sticky top-0 z-20"
      >
        <div className="flex items-center gap-3">
          <div
            className="w-8 h-8 rounded-full flex items-center justify-center"
            style={{ background: "#C8A84B22", border: "1px solid #C8A84B44" }}
          >
            <span style={{ color: "#C8A84B", fontSize: 14 }}>F</span>
          </div>
          <span
            style={{
              color: "#f0ead8",
              fontSize: 15,
              letterSpacing: "0.2em",
              textTransform: "uppercase",
              fontFamily: "'Cinzel', serif",
            }}
          >
            ForkLens
          </span>
        </div>
        <button 
          onClick={onReset}
          className="text-[#C8A84B] opacity-40 hover:opacity-100 transition-opacity text-[10px] uppercase font-black tracking-widest"
        >
          Return to Threshold
        </button>
      </nav>

      <div className="flex flex-1 max-w-[1000px] w-full mx-auto px-4 gap-12">
        {/* Chat area */}
        <div className="flex flex-col flex-1 max-w-2xl w-full py-12">
          <div className="flex flex-col gap-10 flex-1">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" && (
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center mr-4 flex-shrink-0 mt-1 shadow-glow-amber-sm"
                  style={{
                    background: "#C8A84B11",
                    border: "1px solid #C8A84B33",
                  }}
                >
                  <span style={{ color: "#C8A84B", fontSize: 12 }}>F</span>
                </div>
              )}
              <div
                className={`relative ${msg.role === "user" ? "user-bubble" : "assistant-bubble"}`}
                style={{
                  maxWidth: "85%",
                }}
              >
                {msg.content}
                {msg.emotion && (
                   <div 
                     className="absolute -top-3 -right-3 px-3 py-1 rounded-full bg-[#0A0E14] border border-[#C8A84B]/40 text-[#C8A84B] text-[8px] uppercase tracking-[0.2em] font-sans shadow-[0_0_15px_rgba(200,168,75,0.3)] z-10 backdrop-blur-md"
                     style={{ animation: 'pop-in 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards' }}
                   >
                      ✦ {msg.emotion} ✦
                   </div>
                )}
              </div>
            </div>
          ))}

          {/* Typing indicator */}
          {isTyping && (
            <div className="flex justify-start">
              <div
                className="w-8 h-8 rounded-full flex items-center justify-center mr-4 flex-shrink-0 mt-1"
                style={{
                  background: "#D4AF3711",
                  border: "1px solid #D4AF3733",
                }}
              >
                <span style={{ color: "#D4AF37", fontSize: 12 }}>F</span>
              </div>
              <div className="flex gap-2 items-center" style={{ paddingTop: 14 }}>
                {[0, 1, 2].map((i) => (
                  <div
                    key={i}
                    style={{
                      width: 4,
                      height: 4,
                      borderRadius: "50%",
                      background: "#C8A84B",
                      opacity: 0.4,
                      animation: `pulse 1.2s ease-in-out ${i * 0.2}s infinite`,
                    }}
                  />
                ))}
              </div>
            </div>
          )}

          <div className="h-32 md:h-40 flex-shrink-0" />
          <div ref={bottomRef} />
        </div>

        {/* Chat input */}
        <div
          className="sticky bottom-0 pt-8 pb-4"
          style={{ background: "#0A0E14" }}
        >
          <div
            className="relative flex items-end rounded-3xl px-6 py-5 glass border-white/5 focus-within:border-[#C8A84B]/30 transition-all duration-500"
          >
            <textarea
              ref={inputRef}
              rows={1}
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                e.target.style.height = 'auto';
                e.target.style.height = `${Math.min(e.target.scrollHeight, 250)}px`;
              }}
              onKeyDown={handleKeyDown}
              placeholder="Reflect here..."
              className="flex-1 bg-transparent border-none outline-none text-[#f0ead8] text-lg resize-none font-serif italic custom-scrollbar"
              style={{
                lineHeight: 1.6,
                maxHeight: 250,
                minHeight: 32,
              }}
            />
            <button
              onClick={() => handleSend()}
              disabled={!input.trim()}
              className={`ml-4 w-12 h-12 rounded-full flex items-center justify-center transition-all ${
                input.trim() ? "bg-[#C8A84B] text-[#0A0E14]" : "bg-white/5 text-white/10"
              }`}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M5 12h14M12 5l7 7-7 7" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
          <p className="text-center text-[10px] text-white/10 uppercase tracking-[0.5em] mt-6 select-none font-sans">
            Encrypted Reflection Sanctuary
          </p>
        </div>
        </div>

        {/* Emotion Arc Sidebar */}
        <div className="hidden lg:flex flex-col w-72 py-12 border-l border-white/5 pl-10 sticky top-24 h-[calc(100vh-6rem)] overflow-y-auto">
          <div className="text-[10px] text-[#C8A84B] uppercase tracking-[0.3em] mb-10 font-sans opacity-80 flex items-center gap-3">
             <span className="animate-pulse">✦</span> Emotional Arc
          </div>
          <div className="flex flex-col gap-8 relative before:absolute before:inset-y-0 before:left-[11px] before:w-[1px] before:bg-gradient-to-b before:from-[#C8A84B]/30 before:to-transparent">
            {messages.filter(m => m.emotion).map((m, idx) => {
               const msgIndex = messages.findIndex(x => x.id === m.id);
               const relatedQuery = msgIndex > 0 ? messages[msgIndex - 1].content : "";
               return (
                 <div key={m.id} className="relative z-10 pl-10" style={{ animation: 'pop-in 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards' }}>
                   <div className="absolute left-0 top-1 w-6 h-6 rounded-full bg-[#0A0E14] border border-[#C8A84B]/40 flex items-center justify-center shadow-glow-amber-sm">
                     <span className="w-1.5 h-1.5 rounded-full bg-[#C8A84B]"></span>
                   </div>
                   <div className="text-[9px] font-sans text-[#C8A84B] uppercase tracking-[0.2em] mb-2 opacity-90">
                     {m.emotion}
                   </div>
                   <div className="text-sm text-[#f0ead8] font-serif italic opacity-70 leading-relaxed line-clamp-3">
                     "{relatedQuery}"
                   </div>
                 </div>
               );
            })}
            {messages.filter(m => m.emotion).length === 0 && (
              <div className="text-xs text-white/30 font-serif italic pl-10 opacity-60">
                The path ahead is unwritten. As you share, your emotional journey will be etched here.
              </div>
            )}
          </div>
        </div>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 0.2; transform: scale(0.9); }
          50% { opacity: 0.8; transform: scale(1.1); }
        }
        @keyframes pop-in {
          0% { opacity: 0; transform: scale(0.5) translateY(10px); }
          100% { opacity: 1; transform: scale(1) translateY(0); }
        }
        .custom-scrollbar::-webkit-scrollbar { width: 4px; }
        .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
        .custom-scrollbar::-webkit-scrollbar-thumb { background: rgba(200, 168, 75, 0.2); border-radius: 4px; }
        * { box-sizing: border-box; }
      `}</style>
    </div>
  );
}
