// api.js — Ironclad 2.0 API Client
import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

const API = axios.create({ baseURL: BASE_URL });

// ── Upload a protected asset ──────────────────────────────────────────
export const uploadAsset = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  try {
    const res = await API.post("/upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  } catch (err) {
    const detail = err.response?.data?.detail || "Upload failed";
    return { error: detail };
  }
};

// Legacy alias
export const uploadImage = uploadAsset;

// ── Scan a suspect file ───────────────────────────────────────────────
export const checkAsset = async (file) => {
  const formData = new FormData();
  formData.append("file", file);
  try {
    const res = await API.post("/check/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return res.data;
  } catch (err) {
    const detail = err.response?.data?.detail || "Scan failed";
    return { error: detail };
  }
};

// Legacy alias
export const checkImage = checkAsset;

// ── Get all registered assets ─────────────────────────────────────────
export const getAssets = async () => {
  try {
    const res = await API.get("/assets/");
    return res.data;
  } catch (err) {
    return { error: "Could not load assets", assets: [] };
  }
};

// ── Get system stats ──────────────────────────────────────────────────
export const getStats = async () => {
  try {
    const res = await API.get("/stats");
    return res.data;
  } catch (err) {
    return null;
  }
};