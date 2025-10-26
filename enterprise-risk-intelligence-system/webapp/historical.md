# Historical Risk Scores

Coming soon: Historical risk score tracking and trend analysis.

Planned features:

- Time-series storage of calculated risk scores per client.
- Aggregation and trend charts (weekly, monthly, quarterly).
- Filters: client, region, risk category, and date range.
- Export (CSV/Parquet) and alerts for rising risk trends.

Implementation notes:

- Backend: add an endpoint to persist calculated scores (POST `/risk/history`) and a query endpoint (GET `/risk/history?client_id=...`).
- Storage: use a lightweight table in SQLite for dev; support for Postgres for production.
- Frontend: Streamlit page with interactive Plotly time-series charts and statistical summaries.

If you'd like, I can scaffold the backend models and endpoints next (SQLModel model + migration) and wire up the UI to show real historical data.
