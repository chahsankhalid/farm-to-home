# Farm to Home Recharge Add Extras API

A lightweight FastAPI microservice used by the Farm to Home Shopify storefront to allow subscription customers to add and remove extra products from their Recharge subscriptions.

---

## Features

- Add extras to an existing Recharge subscription
- Remove extras from a subscription
- Retrieve current extras for a customer
- Recharge API integration
- CORS support
- Environment variable configuration
- Docker support

---

## Tech Stack

- Python 3.12
- FastAPI
- Recharge API
- Requests
- Docker

---

## Project Structure

```
.
├── config.py
├── Dockerfile
├── main.py
├── recharge.py
├── requirements.txt
├── routes/
├── services/
└── security.py
```

---

## Environment Variables

Create a `.env` file.

```
RECHARGE_API_TOKEN=xxxxxxxxxxxxxxxx
SHOPIFY_STORE=farmtohome.pt
API_KEY=your-secret-key
RECHARGE_BASE_URL=https://api.rechargeapps.com
```

---

## Install

```bash
pip install -r requirements.txt
```

---

## Run

```bash
uvicorn main:app --reload
```

Swagger:

```
http://localhost:8000/docs
```

---

## Docker

Build:

```bash
docker build -t recharge-add-extras .
```

Run:

```bash
docker run --env-file .env -p 8000:8000 recharge-add-extras
```

---

## API Endpoints

### Add Extra

```
POST /subscription/add-extra
```

### Remove Extra

```
DELETE /subscription/remove-extra/{subscription_id}
```

### Get Extras

```
GET /subscription/extras/{shopify_customer_id}
```

---

## License

Internal project for Farm to Home.