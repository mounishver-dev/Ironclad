import React from "react";
import { motion } from "framer-motion";

function ThreatMeter({ level }) {
  const config = {
    High:    { pct: 90, cls: "high",   label: "HIGH THREAT",   color: "#ea4335" },
    Medium:  { pct: 55, cls: "medium", label: "MEDIUM THREAT", color: "#f9ab00" },
    Low:     { pct: 25, cls: "low",    label: "LOW THREAT",    color: "#34a853" },
    Safe:    { pct: 5,  cls: "safe",   label: "SAFE",          color: "#34a853" },
    Unknown: { pct: 40, cls: "medium", label: "UNKNOWN",       color: "#f9ab00" },
  };
  const c = config[level] || config["Unknown"];
  return (
    <div className="threat-meter">
      <div className="threat-meter-label">
        <span>Threat Level</span>
        <span style={{ color: c.color, fontWeight: 700, fontFamily: "'Google Sans', sans-serif" }}>{c.label}</span>
      </div>
      <div className="threat-bar-track">
        <motion.div
          className={`threat-bar-fill ${c.cls}`}
          initial={{ width: 0 }}
          animate={{ width: `${c.pct}%` }}
          transition={{ duration: 1.2, ease: "easeOut", delay: 0.3 }}
        />
      </div>
      <div className="threat-labels">
        <span>Safe</span><span>Low</span><span>Medium</span><span>High</span>
      </div>
    </div>
  );
}

function ActionPill({ action }) {
  const map = {
    "Immediate Takedown": { cls: "takedown", icon: "🚨" },
    "Legal Review":       { cls: "legal",    icon: "⚖️" },
    "Monitor":            { cls: "monitor",  icon: "👁️" },
    "No Action":          { cls: "none",     icon: "✅" },
  };
  const m = map[action] || { cls: "monitor", icon: "📋" };
  return (
    <div className={`action-pill ${m.cls}`}>
      {m.icon} {action || "Manual Review"}
    </div>
  );
}

function ScoreCard({ label, value, colorClass }) {
  return (
    <div className="score-card">
      <div className="score-label">{label}</div>
      <motion.div
        className={`score-value ${colorClass}`}
        initial={{ opacity: 0, scale: 0.75 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ type: "spring", stiffness: 280 }}
      >
        {value ?? "—"}
      </motion.div>
    </div>
  );
}

export default function Result({ result }) {
  if (!result) return null;

  const isUnauthorized = result.status === "Unauthorized";
  const isReview = result.status === "Review Required";
  const isSafe = result.status === "Safe";

  const headerCls = isUnauthorized ? "unauthorized" : isReview ? "review" : "safe";
  const statusIcon = isUnauthorized ? "🚨" : isReview ? "⚠️" : "✅";
  const titleCls = isUnauthorized ? "unauthorized" : isReview ? "review" : "safe";

  const ai = result.ai_forensics || {};
  const sim = result.similarity || {};
  const threatLevel = result.threat_level || ai.threat_level || "Unknown";

  const compositeScore = sim.composite_score != null
    ? `${Math.round(sim.composite_score * 100)}%`
    : null;

  const scoreColor = (s) => {
    if (s == null) return "blue";
    return s >= 0.9 ? "high" : s >= 0.75 ? "medium" : "low";
  };

  return (
    <div className="result-panel">
      {/* Header */}
      <div className={`result-header ${headerCls}`}>
        <motion.span
          className="result-status-icon"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ type: "spring", stiffness: 260, damping: 18 }}
        >
          {statusIcon}
        </motion.span>
        <div>
          <div className={`result-status-title ${titleCls}`}>{result.status}</div>
          {result.matched_asset && (
            <div style={{ fontSize: "0.82rem", color: "#5f6368", marginTop: 2 }}>
              Matched:{" "}
              <strong style={{ color: "#202124", fontFamily: "'Google Sans', sans-serif" }}>
                {result.matched_asset.filename}
              </strong>
            </div>
          )}
          {isSafe && (
            <div style={{ fontSize: "0.82rem", color: "#5f6368", marginTop: 2 }}>{result.message}</div>
          )}
        </div>
      </div>

      <div className="result-body">
        {/* Threat Meter */}
        {!isSafe && <ThreatMeter level={threatLevel} />}

        {/* Similarity Scores */}
        {!isSafe && sim.composite_score != null && (
          <div>
            <p className="section-title">Similarity Analysis</p>
            <div className="scores-grid">
              <ScoreCard label="Composite Score" value={compositeScore} colorClass={scoreColor(sim.composite_score)} />
              <ScoreCard label="pHash Distance"  value={sim.phash_distance ?? "—"}
                colorClass={sim.phash_distance < 15 ? "high" : sim.phash_distance < 35 ? "medium" : "low"} />
              <ScoreCard label="dHash Distance"  value={sim.dhash_distance ?? "—"}
                colorClass={sim.dhash_distance < 15 ? "high" : "medium"} />
              <ScoreCard label="Histogram Match" value={sim.histogram_similarity != null
                ? `${(sim.histogram_similarity * 100).toFixed(0)}%` : "—"} colorClass="blue" />
            </div>
          </div>
        )}

        {/* Modifications */}
        {ai.modifications_detected?.length > 0 && (
          <div>
            <p className="badges-title">Modifications Detected</p>
            <div className="badges-list">
              {ai.modifications_detected.map((mod, i) => (
                <motion.span
                  key={i}
                  className="badge badge-mod"
                  initial={{ opacity: 0, x: -6 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.06 }}
                >
                  ✂️ {mod}
                </motion.span>
              ))}
            </div>
          </div>
        )}

        {/* Gemini AI Report */}
        {Object.keys(ai).length > 0 && ai._analysis_status !== "error" && (
          <div className="ai-card">
            <div className="ai-card-header">
              <span style={{ color: "#1a73e8", fontSize: "0.95rem" }}>✦</span>
              <span className="ai-card-title">Gemini AI Forensic Report</span>
              {ai._model_used && (
                <span style={{ fontSize: "0.65rem", color: "#5f6368", marginLeft: "auto" }}>
                  via {ai._model_used}
                </span>
              )}
            </div>
            <div className="ai-card-body">
              {ai.verdict && (
                <div className="ai-field">
                  <span className="ai-field-label">Verdict</span>
                  <div className="ai-verdict">{ai.verdict}</div>
                </div>
              )}

              {ai.confidence != null && (
                <div className="ai-field">
                  <span className="ai-field-label">Confidence</span>
                  <div className="ai-confidence">
                    <div className="confidence-bar-track">
                      <motion.div
                        className="confidence-bar-fill"
                        initial={{ width: 0 }}
                        animate={{ width: `${ai.confidence}%` }}
                        transition={{ duration: 1, delay: 0.4 }}
                      />
                    </div>
                    <span className="confidence-pct">{ai.confidence}%</span>
                  </div>
                </div>
              )}

              {ai.recommended_action && (
                <div className="ai-field">
                  <span className="ai-field-label">Recommended Action</span>
                  <ActionPill action={ai.recommended_action} />
                </div>
              )}

              {ai.piracy_type && ai.piracy_type !== "None" && (
                <div className="ai-field">
                  <span className="ai-field-label">Piracy Classification</span>
                  <span className="badge badge-warn">⚠️ {ai.piracy_type}</span>
                </div>
              )}

              {ai.evidence?.length > 0 && (
                <div className="ai-field">
                  <span className="ai-field-label">Forensic Evidence</span>
                  <ul style={{ paddingLeft: 16, margin: 0, display: "flex", flexDirection: "column", gap: 4 }}>
                    {ai.evidence.map((ev, i) => (
                      <li key={i} style={{ fontSize: "0.82rem", color: "#5f6368" }}>{ev}</li>
                    ))}
                  </ul>
                </div>
              )}

              {ai.summary && (
                <div className="ai-field">
                  <span className="ai-field-label">Summary</span>
                  <p className="ai-field-value">{ai.summary}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Performance */}
        {result.performance && (
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap", fontSize: "0.75rem" }}>
            <span className="badge badge-info">⚡ {result.performance.total_time_ms}ms total</span>
            {result.performance.fetch_time_ms && (
              <span className="badge badge-info">🌐 {result.performance.fetch_time_ms}ms fetch</span>
            )}
            {result.performance.assets_scanned != null && (
              <span className="badge badge-info">🗄️ {result.performance.assets_scanned} assets scanned</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}