import numpy as np


def build_payment_fraud_features(
    request_body: dict
) -> np.ndarray:
   

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

    features = [0.0] * 30
    features[0] = time_feature
    features[29] = amount_feature

    return np.array(
        features
    ).reshape(1, -1)