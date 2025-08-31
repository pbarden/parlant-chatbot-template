# Installation

## Prerequisites

* Docker and Docker Compose installed.
* Python 3.11+ (optional, only if you plan to run without Docker).
* Node.js (optional, only if you want to run the simple static server in `frontend/`).
* A running Parlant server (default assumed at `http://localhost:8800`).
* An OpenAI API key if your Parlant agent requires one.

---

## Steps

### 1) Open the canvas “Parlant Chatbot Template (FastAPI + JS Widget)”

* Review the project tree and files.

### 2) Copy the repo tree into your project

* Copy the entire structure, preserving `backend/`, `frontend/`, and `ops/` directories.

### 3) Backend setup

#### 3.1) Create environment file

```bash
cd backend
cp .env.example .env
```

* Fill **every** value in `backend/.env`.

  * `APP_SQLALCHEMY_DATABASE_URI`: e.g. `postgresql+psycopg://postgres:postgres@db:5432/chatdb`
  * `APP_PARLANT_BASE_URL`: e.g. `http://localhost:8800`
  * `APP_OPENAI_API_KEY`: your OpenAI key if applicable
  * `APP_PUBLIC_TOKEN_SECRET`: a long random string
  * `APP_BACKEND_CORS_ORIGINS`: JSON array of allowed origins for your sites

#### 3.2) Start services

```bash
docker compose up -d --build
```

#### 3.3) Run database migrations

```bash
docker compose exec api alembic upgrade head
```

#### 3.4) Create a client tenant

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "slug": "acme",
    "name": "Acme",
    "parlant_base_url": "http://localhost:8800",
    "openai_api_key": "YOUR_OPENAI_KEY"
  }' \
  http://localhost:8000/api/v1/clients
```

* Save the `slug` you choose (e.g., `acme`).
* Ensure your Parlant server has an **Agent ID** ready (replace `YOUR_AGENT_ID` later).

### 4) Frontend configuration

* Edit `frontend/public/index.html`:

```html
<script type="module" src="/static/chatbot-widget.js"></script>
<parlant-chat
  server="http://localhost:8000/api/v1"
  client-slug="acme"
  agent-id="YOUR_AGENT_ID"
  float
  open
></parlant-chat>
```

### 5) Place the widget on the client site

* Include the web component bundle and the `<parlant-chat …>` element on the client’s website.
* The widget will:

  * create/resume a session via your FastAPI layer,
  * persist `public_token` and `last_offset` in `localStorage`,
  * send messages to `/public/events/send/{public_token}`,
  * long-poll `/public/events/stream/{public_token}` for `message` and `status`,
  * log all events to Postgres for measurement.

### 6) Deploy

* Swap DB URI, CORS, and secrets in `.env`.
* Build and run the API container; serve `frontend/public` on the client domain; keep `server` pointing to your API base (e.g., `https://api.yourdomain.com/api/v1`).

---

# Installation Checklist

1. Clone repo.
2. `cd backend && cp .env.example .env`.
3. Edit `.env` values.
4. `docker compose up -d --build` **under** `backend/`.
5. `docker compose exec api alembic upgrade head`.
6. Create client via API call.
7. Open `frontend/public/index.html` from a static server.
8. Place widget on client site; set attributes: `server`, `client-slug`, `agent-id`.

---

## Verification

* Health check:

```bash
curl http://localhost:8000/api/v1/healthz
```

* Client created (list via DB or re-POST with same slug to confirm uniqueness).
* Open the demo page (`frontend/public/index.html`) and send a message; verify events appear in DB.

## Notes

* Keep `APP_PUBLIC_TOKEN_SECRET` secret. Rotate when needed.
* Ensure `APP_BACKEND_CORS_ORIGINS` includes all site origins that will embed the widget.
* If Parlant runs on a different host, set `APP_PARLANT_BASE_URL` accordingly.

## Troubleshooting

* **CORS error**: add your site origin to `APP_BACKEND_CORS_ORIGINS` and restart.
* **Database connection failed**: check `APP_SQLALCHEMY_DATABASE_URI`, confirm Postgres is up, re-run migrations.
* **Invalid agent id**: confirm the Agent ID exists on the Parlant server.
* **Session token invalid**: clear browser `localStorage` for keys starting with `parlant:` and reload.
* **Widget not loading**: verify the `<script type="module" src="/static/chatbot-widget.js"></script>` path and that static files are served.
