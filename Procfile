web: gunicorn "backend.app:create_app()" --bind 0.0.0.0:$PORT --workers 4 --timeout 120
streamlit: streamlit run frontend/app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
