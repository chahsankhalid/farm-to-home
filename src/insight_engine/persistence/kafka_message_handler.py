import json
import logging
import numpy as np

from insight_engine.model import model

logger = logging.getLogger(__name__)


async def handle_kafka_message(
    topic: str,
    kafka_values: list[dict],
    kafka_headers: list[dict] | None = None
):
    if not topic.endswith('.http-transactions.v0'):
        logger.warning(
            f'No handler registered for topic: {topic}'
        )
        return

    for transaction in kafka_values:
        try:
            request_headers_raw = transaction.get(
                "requestHeaders"
            )
            request_body_raw = transaction.get(
                "requestBody"
            )

            if (
                not request_headers_raw
                or not request_body_raw
            ):
                logger.warning(
                    "Missing requestHeaders or requestBody"
                )
                continue

            # requestHeaders is stringified JSON
            request_headers = json.loads(
                request_headers_raw
            )

            raw_uri = request_headers.get(
                "Raw-Request-URI"
            )

            # Only score payment fraud requests
            if raw_uri != "/payment-fraud-score":
                continue

            logger.info(
                "Processing payment-fraud-score request"
            )

            # requestBody is stringified JSON
            request_body = json.loads(
                request_body_raw
            )

            logger.info(
                f"Request body keys: "
                f"{list(request_body.keys())}"
            )

            # -------------------------
            # Feature Mapping
            # -------------------------
            # Model expects:
            # Time + V1..V28 + Amount
            # = 30 features

            time_feature = float(
                request_body.get(
                    "timestamp",
                    0.0
                )
            )

            amount_feature = float(
                request_body.get(
                    "euramount",
                    0.0
                )
            )

            # Build 30-feature vector
            features = [0.0] * 30

            # Time
            features[0] = time_feature

            # Amount
            features[29] = amount_feature

            arr = np.array(features).reshape(
                1, -1
            )

            logger.info(
                f"Built feature vector: "
                f"Time={time_feature}, "
                f"Amount={amount_feature}"
            )

            # -------------------------
            # Scoring
            # -------------------------
            prediction = int(
                model.predict(arr)[0]
            )

            probability = (
                float(
                    max(
                        model.predict_proba(arr)[0]
                    )
                )
                if hasattr(
                    model,
                    "predict_proba"
                )
                else 0.0
            )

            logger.info(
                f"Prediction={prediction}, "
                f"probability={probability}"
            )

        except Exception as e:
            logger.exception(
                f"Failed processing Kafka "
                f"message: {e}"
            )