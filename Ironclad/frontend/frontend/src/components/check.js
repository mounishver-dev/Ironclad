import React, { useState } from "react";
import { checkImage } from "../api";
import Result from "./Result";

const Check = () => {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFile(e.target.files[0]);
    setResult(null);
  };

  const handleCheck = async () => {
    if (!file) {
      alert("Please select a file");
      return;
    }

    setLoading(true);

    const response = await checkImage(file);

    setResult(response);
    setLoading(false);
  };

  return (
    <div style={styles.container}>
      <h2>🔍 Check Image Similarity</h2>

      <input type="file" onChange={handleChange} />

      <button onClick={handleCheck} style={styles.button}>
        {loading ? "Checking..." : "Check"}
      </button>

      {/* ✅ Clean UI Component */}
      <Result result={result} />
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
    backgroundColor: "#2196F3",
    color: "white",
    border: "none",
    borderRadius: "5px",
  },
};

export default Check;