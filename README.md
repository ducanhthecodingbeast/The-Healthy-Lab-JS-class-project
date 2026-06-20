<div align="center">
  <h2 align="center">The Healthy Lab</h2>

  The Healthy Lab is a fully responsive healthy food website, <br />built using HTML, CSS, and JavaScript.

  <a href="https://ducanhthecodingbeast.github.io/The-Heallthy-Lab/"><strong>➥ Live Demo</strong></a>

</div>

<br />

### Run Locally

To run **The Healthy Lab** locally, run this command in your terminal:

```bash
git clone https://github.com/ducanhthecodingbeast/The-Heallthy-Lab.git
```

### Live Demo (GitHub Pages)

To view the live demo online, this project uses GitHub Pages. 
If the link above doesn't work yet, make sure GitHub Pages is enabled in your repository settings!

### Run With Docker

From the project folder, run:

```bash
docker compose up --build
```

Then open:

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

Seed backend mock data:

```bash
docker compose exec backend python seed.py
```

You can also build and run without Compose:

```bash
docker build -t the-healthy-lab .
docker run --rm -p 5500:5500 the-healthy-lab
```

### VS Code Live Server

The Live Server port is set to `5501` in `.vscode/settings.json` to avoid colliding with Docker on `5500`, so **Go Live** opens the site at:

```text
http://localhost:5501
```

### Backend

The backend is a simple FastAPI + SQLite API for a school project. It uses Python, FastAPI, SQLAlchemy, SQLite, passlib bcrypt password hashing, and simple bearer-token authentication.

It supports:

- Register and login
- Token-based authentication
- Products
- Orders
- Customer, chef, delivery, and admin roles
- Seed data for testing

Seeded login accounts:

| Role | Email | Password |
| --- | --- | --- |
| Admin | admin@healthylab.test | password123 |
| Chef | chef@healthylab.test | password123 |
| Delivery | delivery@healthylab.test | password123 |
| Customer | customer@healthylab.test | password123 |

Run only the backend locally:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed.py
uvicorn main:app --reload
```

Backend endpoint summary:

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`
- `GET /products`
- `GET /products/{product_id}`
- `POST /products`
- `PUT /products/{product_id}`
- `POST /orders`
- `GET /orders/my`
- `GET /orders`
- `GET /orders/{order_id}`
- `PUT /orders/{order_id}/status`
- `GET /users`
- `GET /admin/summary`

Frontend integration is intentionally not implemented in this backend-only pass. The next frontend coding agent should read [FRONTEND_AGENT_TASKS.md](./docs/frontend/FRONTEND_AGENT_TASKS.md).

More manual API tests are in [TESTING.md](./TESTING.md).
