import hashlib
import hmac

from fastapi import HTTPException, Request

from config import SHOPIFY_API_SECRET


async def verify_shopify_proxy(request: Request):

    params = dict(request.query_params)

    signature = params.pop("signature", None)

    if not signature:
        raise HTTPException(
            status_code=401,
            detail="Missing Shopify signature."
        )

    message = "&".join(
        f"{k}={v}"
        for k, v in sorted(params.items())
    )

    digest = hmac.new(
        SHOPIFY_API_SECRET.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(digest, signature):
        raise HTTPException(
            status_code=401,
            detail="Invalid Shopify signature."
        )