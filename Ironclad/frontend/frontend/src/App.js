import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import "./index.css";

import Header from "./components/Header";
import RegisterAsset from "./components/RegisterAsset";
import ScanAsset from "./components/ScanAsset";
import Dashboard from "./components/Dashboard";

const TABS = [
  { id: "register",  icon: "🛡️", text: "Register Asset" },
  { id: "scan",      icon: "🔍", text: "Scan for Piracy" },
  { id: "dashboard", icon: "📊", text: "Dashboard" },
];

const PAGE_VARIANTS = {
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0, transition: { duration: 0.25, ease: "easeOut" } },
  exit:    { opacity: 0, y: -8, transition: { duration: 0.18 } },
};

/* ── Feature card data ─────────────────────────────────────────────── */
const FEATURES = [
  {
    icon: "🧬",
    iconColor: "green",
    title: "4-Hash Digital DNA",
    desc: (
      <>
        Uses <span style={{ color: "#1a73e8" }}>pHash, dHash, aHash & wHash</span> as
        a composite fingerprint that survives cropping, filtering, and format conversion.
      </>
    ),
  },
  {
    icon: "✦",
    iconColor: "blue",
    iconHex: true,
    title: "Gemini AI Forensics",
    desc: (
      <>
        <span style={{ color: "#1a73e8" }}>Gemini 2.5 Flash</span> acts as a forensic
        agent, producing structured verdicts with evidence, confidence scores, and
        recommended actions.
      </>
    ),
  },
  {
    icon: "⚡",
    iconColor: "red",
    title: "2× Faster Async Scan",
    desc: (
      <>
        All stored assets are fetched <span style={{ color: "#1a73e8" }}>in parallel</span>{" "}
        via async I/O, with a 2-gate filter so Gemini is only called when necessary.
      </>
    ),
  },
];

export default function App() {
  const [activeTab, setActiveTab] = useState("register");

  return (
    <div className="app-wrapper">
      <Header />

      <main className="page-container">
        {/* ── Hero ── */}
        <motion.div
          className="hero"
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
        >
          <div className="hero-eyebrow">
            ✦ Google Build with AI Hackathon
          </div>
          <h1>
            Forensic-Grade{" "}
            <span className="hero-highlight">Asset Protection</span>
          </h1>
          <p>
            Generate a Digital DNA fingerprint for any media asset. Detect
            piracy even through cropping, filters, and format conversion —
            powered by Gemini 2.5 Flash.
          </p>
        </motion.div>

        {/* ── Feature Row ── */}
        <motion.div
          className="feature-row"
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.12 }}
        >
          {FEATURES.map((f) => (
            <div className="feature-card" key={f.title}>
              <div className={`geo-icon ${f.iconColor} ${f.iconHex ? "hex" : ""}`}>
                {f.icon}
              </div>
              <h3>{f.title}</h3>
              <p>{f.desc}</p>
            </div>
          ))}
        </motion.div>

        {/* ── Tab Nav ── */}
        <motion.nav
          className="tab-nav"
          role="tablist"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.18 }}
        >
          {TABS.map((tab) => (
            <button
              key={tab.id}
              id={`tab-${tab.id}`}
              role="tab"
              aria-selected={activeTab === tab.id}
              className={`tab-btn ${activeTab === tab.id ? "active" : ""}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-text">{tab.text}</span>
            </button>
          ))}
        </motion.nav>

        {/* ── Content ── */}
        <AnimatePresence mode="wait">
          {activeTab === "register" && (
            <motion.div
              key="register"
              variants={PAGE_VARIANTS}
              initial="initial"
              animate="animate"
              exit="exit"
              className="content-card"
            >
              <p className="card-title">🛡️ Register Protected Asset</p>
              <p className="card-subtitle">
                Upload an original asset to generate its Digital DNA and add it to
                the protected registry. Supports images, PDF, video, and audio.
              </p>
              <RegisterAsset />
            </motion.div>
          )}

          {activeTab === "scan" && (
            <motion.div
              key="scan"
              variants={PAGE_VARIANTS}
              initial="initial"
              animate="animate"
              exit="exit"
              className="content-card"
            >
              <p className="card-title">🔍 Forensic Piracy Scan</p>
              <p className="card-subtitle">
                Upload a suspect file. Ironclad compares its DNA against all
                protected assets using a 2-gate filter, then invokes Gemini AI
                for a forensic deep-dive.
              </p>
              <ScanAsset />
            </motion.div>
          )}

          {activeTab === "dashboard" && (
            <motion.div
              key="dashboard"
              variants={PAGE_VARIANTS}
              initial="initial"
              animate="animate"
              exit="exit"
              className="content-card"
            >
              <p className="card-title">📊 System Dashboard</p>
              <p className="card-subtitle">
                Overview of the Ironclad protection system, registered assets,
                and AI capabilities.
              </p>
              <Dashboard />
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Footer ── */}
        <div
          style={{
            textAlign: "center",
            marginTop: 36,
            fontSize: "0.78rem",
            color: "#5f6368",
            fontFamily: "'Roboto', sans-serif",
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            gap: 14,
            flexWrap: "wrap",
          }}
        >
          <span>Ironclad v2.0.0</span>
          <span style={{ color: "#dadce0" }}>·</span>
          <span>Powered by <span style={{ color: "#1a73e8", fontWeight: 600 }}>Gemini 2.5 Flash</span></span>
          <span style={{ color: "#dadce0" }}>·</span>
          <span>🔥 Firebase Firestore</span>
          <span style={{ color: "#dadce0" }}>·</span>
          <span>Google Build with AI Hackathon</span>
        </div>
      </main>
    </div>
  );
}