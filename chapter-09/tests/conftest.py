import os
import sys
from pathlib import Path

"""
Общий конфиг для pytest в chapter-09.

Делает две вещи:
- добавляет корень chapter-09 в sys.path, чтобы работал импорт `from app.app import app`
- выставляет SECRET_TOKEN для JWT в тестовой среде
"""

ROOT_DIR = Path(__file__).resolve().parents[1]  # .../chapter-09

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault("SECRET_TOKEN", "test-secret-key")


