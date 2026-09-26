"""Điểm vào cho Vercel (@vercel/python): biến `app` là ứng dụng WSGI."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gpmt import create_app  # noqa: E402

app = create_app()
