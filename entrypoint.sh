set -e

uv run python scripts/setup.py

exec uv run streamlit run demo.py --server.port "${PORT:-8080}" --server.address 0.0.0.0
