1. Copy `.env.example` to `.env` and fill values.
2. `docker compose up -d --build`.
3. Run migrations: `docker compose exec api alembic upgrade head`.
4. Create a client: POST `/api/v1/clients` with `{slug,name,parlant_base_url,openai_api_key}`.
5. Use frontend with `client_slug` and `agent_id`.