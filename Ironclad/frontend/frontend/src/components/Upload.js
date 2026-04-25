import React, { useState } from "react";
import { uploadImage } from "../api";

const Upload = () => {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFile(e.target.files[0]);
    setResponse(null);
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    setLoading(true);

    const result = await uploadImage(file);

    setResponse(result);
    setLoading(false);
  };

  return (
    <div style={styles.container}>
      <h2>📤 Upload Original Image</h2>

      <input type="file" onChange={handleChange} />

      <button onClick={handleUpload} style={styles.button}>
        {loading ? "Uploading..." : "Upload"}
      </button>

      {response && (
        <div style={styles.result}>
          <p><strong>Filename:</strong> {response.filename}</p>
          <p><strong>Status:</strong> {response.message}</p>
          <p><strong>Hash:</strong> {response.hash}</p>
        </div>
      )}
    </div>
  );
};

const styles = {
  container: {
    border: "1px solid #ccc",
    padding: "20px",
    margin: "20px",
    borderRadius: "10px",
    textAlign: "center",
  },
  button: {
    marginTop: "10px",
    padding: "10px 20px",
    cursor: "pointer",
    backgroundColor: "#4CAF50",
    color: "white",
    border: "none",
    borderRadius: "5px",
  },
  result: {
    marginTop: "15px",
    backgroundColor: "#f4f4f4",
    padding: "10px",
    borderRadius: "5px",
  },
};

export default Upload;