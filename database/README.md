# Database notes

Local PostgreSQL is started by `docker compose up -d db` and exposed on port 5433.

The starter uses SQLAlchemy `Base.metadata.create_all()` at API startup for convenience. That is **not** a production migration strategy. Before pilot deployment, add Alembic migrations and a reviewed upgrade/rollback process.

Core entities:
- profiles (maps Supabase user UUID to application role)
- districts, crops, markets, market_prices
- trucks, buyers
- bookings, farmer_offers

Demo price records use `is_demo=true`, `is_verified=false`, `source_type=demo`, and an explicit illustrative source label. Seed truck and buyer rows are unverified, so they do not appear in farmer-facing verified listings by default.
