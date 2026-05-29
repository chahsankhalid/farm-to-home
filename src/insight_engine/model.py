from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).parent.parent.parent / "model/model.pkl"

try:
    model = joblib.load(MODEL_PATH)
except Exception:
    model = None