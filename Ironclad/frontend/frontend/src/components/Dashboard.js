import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getStats, getAssets } from "../api";

/* Google-brand colored icon rows */
const CAPABILITIES = [
  { icon: "🧬", iconColor: "green",  title: "4-Hash DNA",        desc: "pHash + dHash + aHash + wHash composite fingerprinting" },
  { icon: "✦",  iconColor: "blue",   title: "Gemini 2.5 Flash",  desc: "AI forensic agent with structured JSON analysis output" },
  { icon: "⚡",  iconColor: "red",    title: "Async Parallel",    desc: "All stored assets fetched simultaneously via async I/O" },
  { icon: "📁", iconColor: "yellow", title: "Any File Type",     desc: "Images, PDF, video keyframes, and audio spectrograms" },
];

const GOOGLE_STACK = [
  { icon: "✦", color: "#1a73e8", bg: "#e8f0fe", name: "Gemini 2.5 Flash",   role: "AI Forensic Agent" },
  { icon: "🔥", color: "#ea4335", bg: "#fce8e6", name: "Firebase Firestore", role: "Asset Registry" },
  { icon: "📦", color: "#34a853", bg: "#e6f4ea", name: "Google Gen AI SDK",  role: "API Client" },
];

export default function Dashboard() {
  const [stats, setStats]   = useState(null);
  const [assets, setAssets] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      const [s, a] = await Promise.all([getStats(), getAssets()]);
      setStats(s);
      setAssets(a?.assets || []);
      setLoading(false);
    })();
  }, []);

  const statCards = [
    { icon: "🛡️", label: "Protected Assets",      value: stats?.protected_assets ?? assets.length, color: "blue" },
    { icon: "🧬", label: "Hash Algorithms",        value: 4,  color: "green" },
    { icon: "🔬", label: "Similarity Gates",       value: 2,  color: "red" },
    { icon: "📁", label: "File Types Supported",   value: 11, color: "yellow" },
  ];

  return (
    <div>
      {/* Stats */}
      <p className="section-title">System Overview</p>
      <div className="stats-grid">
        {statCards.map((s, i) => (
          <motion.div
            key={s.label}
            className="stat-card"
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07 }}
          >
            <span className="stat-icon">{s.icon}</span>
            <div className={`stat-number ${s.color}`}>{loading ? "—" : s.value}</div>
            <div className="stat-label">{s.label}</div>
          </motion.div>
        ))}
      </div>

      {/* Registered Assets */}
      {assets.length > 0 && (
        <div style={{ marginBottom: 28 }}>
          <p className="section-title">Registered Assets</p>
          <div style={{ display: "flex", flexDirection: "column", gap: 8, maxHeight: 280, overflowY: "auto" }}>
            {assets.map((a, i) => (
              <motion.div
                key={a.filename || i}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.04 }}
                style={{
                  display: "flex", alignItems: "center", gap: 12,
                  background: "#fff",
                  border: "1px solid #dadce0",
                  borderRadius: 10,
                  padding: "10px 14px",
                  boxShadow: "0 1px 3px rgba(0,0,0,0.06)",
                }}
              >
                <span style={{ fontSize: "1.1rem" }}>
                  {a.file_type === "video" ? "🎥"
                    : a.file_type === "audio" ? "🎵"
                    : a.file_type === "pdf"   ? "📄"
                    : "🖼️"}
                </span>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: "0.875rem", fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap", fontFamily: "'Google Sans', sans-serif" }}>
                    {a.filename}
                  </div>
                  <div style={{ fontSize: "0.7rem", color: "#5f6368" }}>
                    {a.file_type} · {a.upload_date ? new Date(a.upload_date).toLocaleDateString() : "—"}
                  </div>
                </div>
                <span
                  className="badge"
                  style={{
                    fontSize: "0.65rem",
                    background: a.has_multi_hash ? "#e6f4ea" : "#fef7e0",
                    border: `1px solid ${a.has_multi_hash ? "#ceead6" : "#fde9a2"}`,
                    color: a.has_multi_hash ? "#137333" : "#9c4f00",
                  }}
                >
                  {a.has_multi_hash ? "✓ DNA v2" : "Hash v1"}
                </span>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Capabilities — Google card style */}
      <p className="section-title">System Capabilities</p>
      <div className="feature-row" style={{ marginBottom: 28 }}>
        {CAPABILITIES.map((c, i) => (
          <motion.div
            key={c.title}
            className="feature-card"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 + i * 0.07 }}
          >
            <div className={`geo-icon ${c.iconColor}`}>{c.icon}</div>
            <h3>{c.title}</h3>
            <p>{c.desc}</p>
          </motion.div>
        ))}
      </div>

      {/* Google Stack */}
      <p className="section-title">Powered by Google</p>
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        {GOOGLE_STACK.map((g) => (
          <div
            key={g.name}
            style={{
              flex: "1 1 180px",
              display: "flex", gap: 12, alignItems: "center",
              background: "#fff",
              border: "1px solid #dadce0",
              borderRadius: 12,
              padding: "14px 16px",
              boxShadow: "0 1px 3px rgba(0,0,0,0.08)",
            }}
          >
            <div
              style={{
                width: 40, height: 40, borderRadius: "50%",
                background: g.bg,
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "1.15rem", flexShrink: 0,
              }}
            >
              {g.icon}
            </div>
            <div>
              <div style={{ fontSize: "0.875rem", fontWeight: 700, color: g.color, fontFamily: "'Google Sans', sans-serif" }}>
                {g.name}
              </div>
              <div style={{ fontSize: "0.75rem", color: "#5f6368" }}>{g.role}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
