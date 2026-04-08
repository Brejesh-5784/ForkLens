import React, { useState, useEffect } from "react";

const SendIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" />
  </svg>
);

const TICKER_FACTS = [
  "Anna Karenina faced her crossroads on a Moscow platform",
  "Hamlet questioned every choice before acting",
  "Raskolnikov wrestled his conscience across 500 pages",
  "Jane Eyre chose dignity over desire at every turn",
  "Emma Bovary dreamed of a life beyond her station",
  "Dorothea Brooke sought a life worthy of her ideals",
];

export default function LandingPage({ 
  handleSend, 
  setStarted 
}) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    setTimeout(() => setVisible(true), 100);
  }, []);

  return (
    <div className="lp-root h-screen w-full flex flex-col items-center justify-center relative overflow-hidden">
      {/* Background Decor */}
      <div className="glow-threshold" />
      <div className="constellation" />
      
      {/* Content Container */}
      <div className="relative z-10 w-full max-w-5xl px-8 flex flex-col items-center gap-12">
        
        {/* Header Section */}
        <header className="flex flex-col items-center text-center gap-6">
          <div className={`lp-eyebrow lp-reveal d1 ${visible ? "in" : ""}`}>
            <div className="lp-rule" />
            <span>Archive of Human Crossroads</span>
            <div className="lp-rule r" />
          </div>
          
          <h1 className={`lp-h1 lp-reveal d2 ${visible ? "in" : ""}`}>
            Where Your Story <br />
            <em>Meets the Classics</em>
            <span className="lp-h1-sub">Literary Wisdom for the Modern Soul</span>
          </h1>

          <p className={`lp-sub lp-reveal d3 ${visible ? "in" : ""}`}>
            Share what weighs on you. ForkLens finds the literary character who has already walked your path — and survived it.
          </p>
        </header>

        {/* Ornament Splitter */}
        <div className={`lp-ornament lp-reveal d3 ${visible ? "in" : ""}`}>
          <div className="lp-orn-rule" />
          <span>✦ ✦ ✦</span>
          <div className="lp-orn-rule r" />
        </div>

        {/* Main CTA: Let's Start (Replaces Portals) */}
        <div className={`lp-reveal d4 ${visible ? "in" : ""}`}>
          <button 
            className="lp-start-btn shadow-glow-amber-lg" 
            onClick={() => setStarted(true)}
            style={{ 
              padding: '16px 48px',
              fontSize: '21px',
              marginTop: '10px'
            }}
          >
            Let's Start !!!
          </button>
          <div className="text-[10px] text-white/20 uppercase tracking-[0.5em] mt-8 text-center font-sans animate-pulse">
            the archive of souls awaits
          </div>
        </div>

        {/* Statistics / Footer Content */}
        <div className={`lp-stats lp-reveal d6 ${visible ? "in" : ""}`}>
            <div className="lp-stat">
              <div className="lp-stat-n">93</div>
              <div className="lp-stat-l">Emotion Classes</div>
            </div>
            <div className="lp-stat-div" />
            <div className="lp-stat">
              <div className="lp-stat-n">8</div>
              <div className="lp-stat-l">Macro Categories</div>
            </div>
            <div className="lp-stat-div" />
            <div className="lp-stat">
              <div className="lp-stat-n">50</div>
              <div className="lp-stat-l">Classic Works</div>
            </div>
            <div className="lp-stat-div" />
            <div className="lp-stat">
              <div className="lp-stat-n">RoBERTa</div>
              <div className="lp-stat-l">Emotion Engine</div>
            </div>
        </div>
      </div>

      {/* Ticker Footer */}
      <footer className="absolute bottom-0 w-full lp-ticker">
        <div className="lp-ticker-inner">
          {[...TICKER_FACTS, ...TICKER_FACTS].map((fact, i) => (
            <div key={i} className="lp-ticker-item">
              <span className="lp-ticker-dot">✦</span> {fact}
            </div>
          ))}
        </div>
      </footer>

      <style>{`
        .lp-root { background: transparent; }
        
        .lp-reveal {
          opacity: 0;
          transform: translateY(20px);
          transition: all 1.2s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .lp-reveal.in { opacity: 1; transform: translateY(0); }
        .d1 { transition-delay: 0.1s; }
        .d2 { transition-delay: 0.2s; }
        .d3 { transition-delay: 0.3s; }
        .d4 { transition-delay: 0.4s; }
        .d5 { transition-delay: 0.5s; }
        .d6 { transition-delay: 0.6s; }

        .lp-eyebrow {
          display: flex;
          align-items: center;
          gap: 14px;
          font-family: 'Cinzel', serif;
          font-size: 9.5px;
          letter-spacing: 0.48em;
          text-transform: uppercase;
          color: #C8A84B;
        }
        .lp-rule { width: 36px; height: 1px; background: linear-gradient(90deg, transparent, rgba(200,168,75,0.5)); }
        .lp-rule.r { background: linear-gradient(90deg, rgba(200,168,75,0.5), transparent); }

        .lp-h1 {
          font-family: 'Cormorant Garamond', serif;
          font-size: clamp(3rem, 6vw, 5.5rem);
          font-weight: 300;
          line-height: 1.05;
          color: #f0ead8;
          text-align: center;
        }
        .lp-h1 em { font-style: italic; color: #C8A84B; }
        .lp-h1-sub {
          display: block;
          font-style: italic;
          font-size: 1.2rem;
          color: rgba(240,234,216,0.3);
          margin-top: 10px;
          letter-spacing: 0.1em;
        }

        .lp-sub {
          font-family: 'EB Garamond', serif;
          font-style: italic;
          font-size: 1.15rem;
          color: rgba(240,234,216,0.4);
          max-width: 600px;
          line-height: 1.6;
        }

        .lp-ornament {
          display: flex;
          align-items: center;
          gap: 14px;
          color: rgba(200,168,75,0.3);
        }
        .lp-orn-rule { width: 100px; height: 1px; background: linear-gradient(90deg, transparent, rgba(200,168,75,0.2)); }
        .lp-orn-rule.r { background: linear-gradient(90deg, rgba(200,168,75,0.2), transparent); }

        /* Pathway Grid */
        .lp-pathway-grid {
          display: grid;
          grid-template-columns: repeat(2, 1fr);
          gap: 20px;
          width: 100%;
          max-width: 720px;
        }
        @media (max-width: 640px) { .lp-pathway-grid { grid-template-columns: 1fr; } }

        .lp-path-btn {
          background: rgba(22, 27, 34, 0.4);
          border: 1px solid rgba(200, 168, 75, 0.1);
          padding: 24px;
          border-radius: 8px;
          text-align: center;
          transition: all 0.4s;
          cursor: pointer;
          backdrop-filter: blur(10px);
        }
        .lp-path-btn:hover {
          border-color: rgba(200, 168, 75, 0.4);
          transform: translateY(-5px);
          background: rgba(200, 168, 75, 0.03);
        }

        .lp-path-title {
          display: block;
          font-family: 'Cinzel', serif;
          font-size: 10px;
          letter-spacing: 0.3em;
          text-transform: uppercase;
          color: #C8A84B;
          margin-bottom: 8px;
        }
        .lp-path-desc {
          display: block;
          font-family: 'EB Garamond', serif;
          font-style: italic;
          font-size: 1.2rem;
          color: #f0ead8;
        }
        .lp-path-ornament {
          display: block;
          margin-top: 12px;
          color: rgba(200,168,75,0.2);
        }

        /* Start Button */
        .lp-start-btn {
          background: transparent;
          border: 1px solid #C8A84B;
          color: #C8A84B;
          padding: 16px 40px;
          font-family: 'Cinzel', serif;
          font-size: 13px;
          letter-spacing: 0.4em;
          text-transform: uppercase;
          cursor: pointer;
          transition: all 0.4s;
        }
        .lp-start-btn:hover {
          background: #C8A84B;
          color: #0A0E14;
          box-shadow: 0 0 30px rgba(200, 168, 75, 0.3);
        }

        /* Stats */
        .lp-stats {
          display: flex;
          align-items: center;
          gap: 40px;
          margin-top: 20px;
        }
        .lp-stat-n { font-family: 'Cormorant Garamond', serif; font-size: 1.8rem; color: #C8A84B; }
        .lp-stat-l { font-family: 'Cinzel', serif; font-size: 8px; letter-spacing: 0.2em; color: rgba(240,234,216,0.2); text-transform: uppercase; }
        .lp-stat-div { width: 1px; height: 30px; background: rgba(200,168,75,0.1); }

        .lp-ticker { overflow: hidden; background: rgba(0,0,0,0.2); padding: 12px 0; border-top: 1px solid rgba(255,255,255,0.03); }
        .lp-ticker-inner { display: flex; white-space: nowrap; animation: tick 40s linear infinite; }
        .lp-ticker-item { font-family: 'EB Garamond', serif; font-style: italic; font-size: 0.85rem; color: rgba(240,234,216,0.15); padding: 0 40px; }
        @keyframes tick { from { transform: translateX(0); } to { transform: translateX(-50%); } }
      `}</style>
    </div>
  );
}
