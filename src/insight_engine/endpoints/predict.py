from werkzeug.exceptions import BadRequest, ServiceUnavailable
import numpy as np
from insight_engine.model import model  # make sure this exists

def predict(body):
    if model is None:
        raise ServiceUnavailable("Model not loaded")

    if not body or "features" not in body:
        raise BadRequest("Missing 'features' in request body")

    features = body["features"]

    if not isinstance(features, list):
        raise BadRequest("'features' must be a list")

    arr = np.array(features).reshape(1, -1)

    try:
        pred = int(model.predict(arr)[0])

        if hasattr(model, "predict_proba"):
            prob = float(max(model.predict_proba(arr)[0]))
        else:
            prob = 0.0

        return {
            "prediction": pred,
            "probability": prob
        }

    except Exception:
        raise BadRequest("Prediction failed")