"""Flask API serving the trained task-priority classifier."""
import logging
import sys
from pathlib import Path

import joblib
from flask import Flask, jsonify, request

BASE_DIR = Path(__file__).parent
MODEL_PATH = BASE_DIR / "model.joblib"

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("smart_todo_api")

app = Flask(__name__)
model = joblib.load(MODEL_PATH)
logger.info("Model loaded from %s", MODEL_PATH)

INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Smart Todo API — Priority Predictor</title>
<style>
  :root { color-scheme: light dark; }
  body {
    font-family: system-ui, -apple-system, Segoe UI, sans-serif;
    max-width: 640px; margin: 3rem auto; padding: 0 1.25rem;
    line-height: 1.5;
  }
  h1 { margin-bottom: 0.25rem; }
  .subtitle { color: #666; margin-top: 0; }
  form { display: flex; gap: 0.5rem; margin: 1.5rem 0; }
  input[type=text] {
    flex: 1; padding: 0.6rem 0.75rem; font-size: 1rem;
    border: 1px solid #ccc; border-radius: 6px;
  }
  button {
    padding: 0.6rem 1.1rem; font-size: 1rem; cursor: pointer;
    border: 0; border-radius: 6px; background: #2563eb; color: #fff;
  }
  button:hover { background: #1d4ed8; }
  .examples { font-size: 0.9rem; color: #555; margin-top: -0.5rem; }
  .examples a {
    margin-right: 0.6rem; color: #2563eb; text-decoration: none;
    cursor: pointer;
  }
  .examples a:hover { text-decoration: underline; }
  #result {
    margin-top: 1.5rem; padding: 1rem 1.25rem; border-radius: 8px;
    border: 1px solid #ddd; display: none;
  }
  #result.high   { background: #fef2f2; border-color: #fecaca; color: #991b1b; }
  #result.medium { background: #fffbeb; border-color: #fde68a; color: #92400e; }
  #result.low    { background: #f0fdf4; border-color: #bbf7d0; color: #166534; }
  #result.error  { background: #f3f4f6; border-color: #d1d5db; color: #374151; }
  .priority { font-size: 1.5rem; font-weight: 600; margin: 0; }
  .confidence { margin: 0.25rem 0 0; opacity: 0.8; }
  footer { margin-top: 3rem; font-size: 0.85rem; color: #888; }
  code { background: #f3f4f6; padding: 0.1rem 0.35rem; border-radius: 3px; }
</style>
</head>
<body>
  <h1>Smart Todo API</h1>
  <p class="subtitle">Enter a task and the model will predict its priority.</p>

  <form id="form">
    <input id="task" type="text" placeholder="e.g. Fix login bug before tomorrow demo" autocomplete="off" autofocus>
    <button type="submit">Predict</button>
  </form>

  <div class="examples">
    Try:
    <a data-task="Patch security vulnerability before audit">urgent bug</a>
    <a data-task="Schedule one on one with manager">a meeting</a>
    <a data-task="Read latest tech magazine before bed">leisure reading</a>
  </div>

  <div id="result"></div>

  <footer>
    Backed by <code>POST /predict</code>. See also
    <a href="/health">/health</a>.
  </footer>

<script>
  const form = document.getElementById('form');
  const taskInput = document.getElementById('task');
  const result = document.getElementById('result');

  document.querySelectorAll('.examples a').forEach(a => {
    a.addEventListener('click', () => {
      taskInput.value = a.dataset.task;
      form.requestSubmit();
    });
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const task = taskInput.value.trim();
    if (!task) return;
    result.style.display = 'block';
    result.className = '';
    result.innerHTML = '<p class="priority">Predicting…</p>';
    try {
      const res = await fetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task })
      });
      const data = await res.json();
      if (!res.ok) {
        result.className = 'error';
        result.innerHTML = `<p class="priority">Error</p><p class="confidence">${data.error || res.status}</p>`;
        return;
      }
      result.className = data.priority.toLowerCase();
      const pct = Math.round(data.confidence * 100);
      result.innerHTML = `
        <p class="priority">${data.priority} priority</p>
        <p class="confidence">Model confidence: ${pct}%</p>`;
    } catch (err) {
      result.className = 'error';
      result.innerHTML = `<p class="priority">Network error</p><p class="confidence">${err.message}</p>`;
    }
  });
</script>
</body>
</html>
"""


@app.get("/")
def index():
    return INDEX_HTML, 200, {"Content-Type": "text/html; charset=utf-8"}


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.post("/predict")
def predict():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or "task" not in data:
        return jsonify({"error": "Missing field: task"}), 400

    task = data["task"]
    if not isinstance(task, str) or not task.strip():
        return jsonify({"error": "Missing field: task"}), 400

    probs = model.predict_proba([task])[0]
    idx = int(probs.argmax())
    priority = str(model.classes_[idx])
    confidence = round(float(probs[idx]), 2)

    logger.info("Prediction task=%r -> priority=%s confidence=%.2f",
                task, priority, confidence)

    return jsonify({"priority": priority, "confidence": confidence}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
