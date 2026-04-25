import React, { useState, useCallback, useEffect } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Search, AlertCircle, FileImage, FileVideo, FileAudio, File } from "lucide-react";
import { checkAsset } from "../api";
import Result from "./Result";

const ACCEPTED_TYPES = {
  "image/*": [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".avif"],
  "application/pdf": [".pdf"],
  "video/*": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
  "audio/*": [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"],
};

const SCAN_STAGES = [
  { label: "Extracting Digital DNA…",   progress: 20,  icon: "🔬" },
  { label: "Running Multi-Hash Gates…", progress: 45,  icon: "🧬" },
  { label: "Comparing to 4 hash types…",progress: 65,  icon: "📊" },
  { label: "Invoking Gemini AI Forensics…", progress: 85, icon: "🤖" },
  { label: "Compiling forensic report…",progress: 96,  icon: "📋" },
];

function getFileIcon(type = "") {
  if (type.startsWith("video")) return <FileVideo size={18} />;
  if (type.startsWith("audio")) return <FileAudio size={18} />;
  if (type.startsWith("image")) return <FileImage size={18} />;
  return <File size={18} />;
}

function formatBytes(b) {
  if (b < 1024) return `${b} B`;
  if (b < 1048576) return `${(b / 1024).toFixed(1)} KB`;
  return `${(b / 1048576).toFixed(2)} MB`;
}

export default function ScanAsset() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [stageIdx, setStageIdx] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError]   = useState(null);

  const onDrop = useCallback((accepted) => {
    const f = accepted[0];
    if (!f) return;
    setFile(f);
    setResult(null);
    setError(null);
    if (f.type.startsWith("image")) setPreview(URL.createObjectURL(f));
    else setPreview(null);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxFiles: 1,
  });

  // Animate through stages while loading
  useEffect(() => {
    if (!loading) { setStageIdx(0); return; }
    const timings = [400, 900, 600, 1200, 800];
    let idx = 0;
    const step = () => {
      if (idx < SCAN_STAGES.length - 1) {
        idx++;
        setStageIdx(idx);
        setTimeout(step, timings[idx] || 800);
      }
    };
    const t = setTimeout(step, timings[0]);
    return () => clearTimeout(t);
  }, [loading]);

  const handleScan = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    const res = await checkAsset(file);
    setLoading(false);
    if (res.error) setError(res.error);
    else setResult(res);
  };

  const stage = SCAN_STAGES[stageIdx];
  const ext = file?.name?.split(".").pop()?.toUpperCase() || "";

  return (
    <div>
      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`dropzone-outer ${isDragActive ? "active-drag" : ""} ${file ? "has-file" : ""}`}
        style={{ cursor: loading ? "not-allowed" : "pointer" }}
      >
        <input {...getInputProps()} disabled={loading} id="scan-file-input" />

        <AnimatePresence mode="wait">
          {file ? (
            <motion.div
              key="file"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0 }}
            >
              {preview && (
                <img
                  src={preview}
                  alt="suspect"
                  style={{
                    maxHeight: 130, maxWidth: "100%",
                    borderRadius: 8, marginBottom: 12, objectFit: "cover",
                    border: "1px solid rgba(0,212,255,0.2)",
                    opacity: loading ? 0.6 : 1,
                    transition: "opacity 0.3s",
                  }}
                />
              )}
              <div className="file-preview-chip" style={{ borderColor: "rgba(0,212,255,0.3)", color: "var(--accent-blue)" }}>
                {getFileIcon(file.type)}
                <span style={{ maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {file.name}
                </span>
                <span className="file-type-badge">{ext}</span>
                <span style={{ color: "var(--text-muted)", fontSize: "0.7rem" }}>{formatBytes(file.size)}</span>
              </div>
              {!loading && (
                <p style={{ marginTop: 8, fontSize: "0.75rem", color: "var(--text-muted)" }}>
                  Click or drag to replace
                </p>
              )}
            </motion.div>
          ) : (
            <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <span className="dropzone-icon">🔍</span>
              <p className="dropzone-title">
                {isDragActive ? "Drop suspect file to scan" : "Drag & drop a suspect file to scan"}
              </p>
              <p className="dropzone-sub">
                We'll compare its <strong>Digital DNA</strong> against all protected assets.<br />
                Supports images, video, PDF, and audio files.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Scan button */}
      <button
        id="scan-submit-btn"
        className="btn btn-primary"
        onClick={handleScan}
        disabled={!file || loading}
        style={{ background: loading ? "linear-gradient(135deg,#1e293b,#0f172a)" : undefined }}
      >
        {loading ? (
          <>
            <motion.span
              animate={{ rotate: 360 }}
              transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
              style={{ display: "inline-block" }}
            >
              ⚙️
            </motion.span>
            Scanning…
          </>
        ) : (
          <>
            <Search size={17} />
            Run Forensic Scan
          </>
        )}
      </button>

      {/* Scanning animation */}
      <AnimatePresence>
        {loading && (
          <motion.div
            key="scanner"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            style={{ overflow: "hidden" }}
          >
            <div className="scanning-wrapper">
              <div className="scan-rings">
                <div className="scan-ring" />
                <div className="scan-ring" />
                <div className="scan-ring" />
                <div className="scan-center">🔬</div>
              </div>

              <motion.p
                key={stageIdx}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                className="scan-stage-label"
              >
                {stage.icon} {stage.label}
              </motion.p>

              <div className="scan-progress-bar" style={{ width: "100%" }}>
                <motion.div
                  className="scan-progress-fill"
                  animate={{ width: `${stage.progress}%` }}
                  transition={{ duration: 0.6, ease: "easeOut" }}
                />
              </div>

              <p style={{ fontSize: "0.7rem", color: "var(--text-muted)" }}>
                AI-powered forensic analysis in progress…
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="banner banner-error"
            style={{ marginTop: 14 }}
          >
            <AlertCircle size={14} />
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Result */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ type: "spring", stiffness: 200, damping: 22 }}
          >
            <Result result={result} />
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
