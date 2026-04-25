import React, { useState, useEffect } from "react";
import { Shield, Wifi, WifiOff } from "lucide-react";

export default function Header() {
  const [apiOnline, setApiOnline] = useState(null);

  useEffect(() => {
    const check = async () => {
      try {
        const r = await fetch("http://127.0.0.1:8000/health");
        setApiOnline(r.ok);
      } catch {
        setApiOnline(false);
      }
    };
    check();
    const t = setInterval(check, 30000);
    return () => clearInterval(t);
  }, []);

  return (
    <header className="header">
      <div className="header-inner">
        {/* Logo */}
        <div className="logo-group">
          <div className="logo-icon">
            <Shield size={18} color="#fff" />
          </div>
          <div>
            <div className="logo-text">Ironclad</div>
            <div className="logo-tagline">Digital Asset Protection</div>
          </div>
        </div>

        {/* Right side badges */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {/* Gemini badge */}
          <div
            style={{
              fontSize: "0.78rem",
              fontFamily: "'Google Sans', sans-serif",
              fontWeight: 600,
              color: "#1a73e8",
              background: "#e8f0fe",
              border: "1px solid #c5d9f8",
              padding: "5px 12px",
              borderRadius: "40px",
              display: "flex",
              alignItems: "center",
              gap: "5px",
            }}
          >
            <span style={{ fontSize: "0.9rem" }}>✦</span>
            Gemini 2.5 Flash
          </div>

          {/* API Status */}
          {apiOnline === null ? null : apiOnline ? (
            <div className="status-badge">
              <span className="status-dot" />
              <Wifi size={11} />
              API Online
            </div>
          ) : (
            <div
              className="status-badge"
              style={{
                color: "#ea4335",
                background: "#fce8e6",
                borderColor: "#f5c6c2",
              }}
            >
              <WifiOff size={11} />
              API Offline
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
