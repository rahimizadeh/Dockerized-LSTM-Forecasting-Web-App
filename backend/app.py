from __future__ import annotations

import base64
import io
import os
import tempfile

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB

model = joblib.load("model.pkl")
scaler = joblib.load("scaler.pkl")


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/predict")
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded = request.files["file"]
    if not uploaded.filename:
        return jsonify({"error": "No selected file"}), 400
    if not uploaded.filename.lower().endswith(".csv"):
        return jsonify({"error": "Only CSV files are accepted"}), 400

    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
            uploaded.save(tmp)
            temp_path = tmp.name

        df = pd.read_csv(temp_path)
        if df.empty:
            return jsonify({"error": "CSV file is empty"}), 400
        if not all(pd.api.types.is_numeric_dtype(dtype) for dtype in df.dtypes):
            return jsonify({"error": "CSV must contain numeric columns only"}), 400

        data = scaler.transform(df.values)
        predictions = model.predict(data)
        predictions = scaler.inverse_transform(predictions)

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(df.values, label="Actual")
        ax.plot(predictions, label="Predicted")
        ax.legend()
        ax.set_title("Time-series forecast")

        image_buffer = io.BytesIO()
        fig.savefig(image_buffer, format="png", bbox_inches="tight")
        plt.close(fig)
        image_buffer.seek(0)
        image_b64 = base64.b64encode(image_buffer.read()).decode("utf-8")

        return jsonify(
            {
                "predictions": predictions.flatten().tolist(),
                "plot": image_b64,
            }
        )
    except Exception as exc:
        return jsonify({"error": f"Prediction failed: {exc}"}), 400
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"error": "Uploaded file exceeds the 5 MB limit"}), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
