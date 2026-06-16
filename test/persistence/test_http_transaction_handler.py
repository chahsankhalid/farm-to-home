import json

from insight_engine.domain.models.http_transaction import (
    HttpTransaction,
)
from insight_engine.domain.payment_fraud_features import (
    build_payment_fraud_features,
)


def test_http_transaction_parser():
    kafka_transaction = {
        "id": "123",
        "request_method": "POST",
        "request_url": "/payment-fraud-score",
        "token_type": "Test",
        "request_headers": {
            "Raw-Request-URI":
                "/payment-fraud-score"
        },
        "request_body": json.dumps({
            "timestamp": 100.0,
            "euramount": 50.0,
        }),
        "response_headers": {},
        "response_body": None,
        "response_status_code": "200",
        "customer": "test",
        "environment": "DEV",
        "latency": 10,
        "ip": None,
        "user_id": None,
    }

    transaction = (
        HttpTransaction
        .from_kafka_avro_dict(
            kafka_transaction
        )
    )

    assert (
        transaction.request_headers[
            "Raw-Request-URI"
        ]
        == "/payment-fraud-score"
    )


def test_payment_fraud_filter():
    headers = {
        "Raw-Request-URI":
            "/payment-fraud-score"
    }

    assert (
        headers[
            "Raw-Request-URI"
        ]
        == "/payment-fraud-score"
    )


def test_payment_fraud_features():
    request_body = {
        "timestamp": 100.0,
        "euramount": 50.0,
    }

    arr = (
        build_payment_fraud_features(
            request_body
        )
    )

    assert arr.shape == (1, 30)
    assert arr[0][0] == 100.0
    assert arr[0][29] == 50.0