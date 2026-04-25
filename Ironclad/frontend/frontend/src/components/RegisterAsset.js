import React, { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, CheckCircle, AlertCircle, FileImage, FileVideo, FileAudio, File } from "lucide-react";
import { uploadAsset } from "../api";

const ACCEPTED_TYPES = {
  "image/*": [".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".tiff", ".avif"],
  "application/pdf": [".pdf"],
  "video/*": [".mp4", ".mov", ".avi", ".mkv", ".webm"],
  "audio/*": [".mp3", ".wav", ".ogg", ".flac", ".aac", ".m4a"],
};

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

export default function RegisterAsset() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const onDrop = useCallback((accepted) => {
    const f = accepted[0];
    if (!f) return;
    setFile(f);
    setResult(null);
    setError(null);
    if (f.type.startsWith("image")) {
      const url = URL.createObjectURL(f);
      setPreview(url);
    } else {
      setPreview(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_TYPES,
    maxFiles: 1,
  });

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setResult(null);
    const res = await uploadAsset(file);
    setLoading(false);
    if (res.error) {
      setError(res.error);
    } else {
      setResult(res);
    }
  };

  const ext = file?.name?.split(".").pop()?.toUpperCase() || "";

  return (
    <div>
      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={`dropzone-outer ${isDragActive ? "active-drag" : ""} ${file ? "has-file" : ""}`}
      >
        <input {...getInputProps()} id="register-file-input" />

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
                  alt="preview"
                  style={{
                    maxHeight: 140,
                    maxWidth: "100%",
                    borderRadius: 8,
                    marginBottom: 12,
                    objectFit: "cover",
                    border: "1px solid rgba(124,58,237,0.3)",
                  }}
                />
              )}
              <div className="file-preview-chip">
                {getFileIcon(file.type)}
                <span style={{ maxWidth: 200, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {file.name}
                </span>
                <span className="file-type-badge">{ext}</span>
                <span style={{ color: "var(--text-muted)", fontSize: "0.7rem" }}>
                  {formatBytes(file.size)}
                </span>
              </div>
              <p style={{ marginTop: 8, fontSize: "0.75rem", color: "var(--text-muted)" }}>
                Click or drag to replace
              </p>
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <span className="dropzone-icon">🛡️</span>
              <p className="dropzone-title">
                {isDragActive ? "Drop your asset here" : "Drag & drop any file to protect"}
              </p>
              <p className="dropzone-sub">
                <strong>Images</strong> • PDF • <strong>Video</strong> • Audio<br />
                JPEG, PNG, WEBP, MP4, MOV, MP3, PDF and more
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Upload button */}
      <button
        id="register-submit-btn"
        className="btn btn-primary"
        onClick={handleUpload}
        disabled={!file || loading}
      >
        {loading ? (
          <>
            <motion.span
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              style={{ display: "inline-block" }}
            >
              ⚙️
            </motion.span>
            Generating Digital DNA…
          </>
        ) : (
          <>
            <Upload size={17} />
            Register & Protect Asset
          </>
        )}
      </button>

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

      {/* Success */}
      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <div className="banner banner-success" style={{ marginTop: 16 }}>
              <CheckCircle size={14} />
              Asset registered and protected!&nbsp;
              <strong>{result.filename}</strong>
            </div>

            {/* DNA display */}
            {result.digital_dna && (
              <div style={{ marginTop: 14 }}>
                <p className="section-title">Digital DNA Fingerprint</p>
                <div className="dna-grid">
                  {Object.entries(result.digital_dna).map(([key, val]) => (
                    <div className="dna-chip" key={key}>
                      <div className="dna-label">{key.toUpperCase()}</div>
                      <div className="dna-value">{val?.slice(0, 32)}…</div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Meta row */}
            <div
              style={{
                marginTop: 12,
                display: "flex",
                gap: 10,
                flexWrap: "wrap",
                fontSize: "0.75rem",
                color: "var(--text-muted)",
              }}
            >
              {result.file_type && (
                <span className="badge badge-info">Type: {result.file_type}</span>
              )}
              {result.processing_time_ms && (
                <span className="badge badge-info">⚡ {result.processing_time_ms}ms</span>
              )}
              {result.file_size_bytes && (
                <span className="badge badge-info">{formatBytes(result.file_size_bytes)}</span>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
