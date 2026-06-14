# The Healthy Lab Backend Testing

This is a simple manual checklist for the FastAPI backend.

## Start The App

```bash
docker compose up --build
```

Frontend:

```text
http://localhost:5500
```

Backend API:

```text
http://localhost:8000
```

FastAPI docs:

```text
http://localhost:8000/docs
```

## Seed Mock Data

With Docker:

```bash
docker compose exec backend python seed.py
```

Without Docker:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```

## Test Accounts

All seeded accounts use this password:

```text
password123
```

| Role | Email |
| --- | --- |
| Admin | admin@healthylab.test |
| Chef | chef@healthylab.test |
| Delivery | delivery@healthylab.test |
| Customer | customer@healthylab.test |

## Curl Examples

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"customer@healthylab.test","password":"password123"}'
```

Save the token:

```bash
TOKEN="paste-token-here"
```

### Get Products

```bash
curl http://localhost:8000/products
```

### Create Order

```bash
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "customer_name": "Customer",
    "customer_phone": "0900000004",
    "delivery_address": "123 Green Street",
    "note": "Please deliver after 6 PM",
    "items": [
      {"product_id": 1, "quantity": 1, "custom_details": "Extra avocado"},
      {"product_id": 8, "quantity": 2},
      {
        "product_name": "Custom Food Lab Bowl",
        "quantity": 1,
        "unit_price": 12.5,
        "total_price": 12.5,
        "custom_details": "{\"base\":\"brown rice\",\"protein\":\"grilled chicken\",\"sauce\":\"lemon tahini\"}"
      }
    ]
  }'
```

### Get My Orders

```bash
curl http://localhost:8000/orders/my \
  -H "Authorization: Bearer $TOKEN"
```

### Update Order Status

Login as chef first:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"chef@healthylab.test","password":"password123"}'
```

Then update a pending order to preparing:

```bash
CHEF_TOKEN="paste-chef-token-here"

curl -X PUT http://localhost:8000/orders/1/status \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $CHEF_TOKEN" \
  -d '{"status":"preparing"}'
```

## Manual Checklist

- Register a new customer with `POST /auth/register`.
- Login with each seeded role.
- Confirm `GET /auth/me` returns the logged-in user.
- Confirm public users can call `GET /products`.
- Confirm admin can create and edit products.
- Confirm customer can create an order.
- Confirm customer can only see their own orders.
- Confirm customer can cancel only a pending order.
- Confirm chef can see pending/preparing orders.
- Confirm chef can change `pending -> preparing -> ready`.
- Confirm delivery can see ready/delivering orders.
- Confirm delivery can change `ready -> delivering -> delivered`.
- Confirm admin can see `/users`, all `/orders`, and `/admin/summary`.
