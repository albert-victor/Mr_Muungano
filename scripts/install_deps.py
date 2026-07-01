"""Install only missing packages from requirements.txt."""
from __future__ import annotations

import subprocess
import sys

REQUIRED = {
    "fastapi": "fastapi>=0.115.0",
    "uvicorn": "uvicorn[standard]>=0.32.0",
    "dotenv": "python-dotenv>=1.0.0",
    "chromadb": "chromadb>=0.5.0",
    "pypdf": "pypdf>=5.0.0",
    "httpx": "httpx>=0.27.0",
    "sentence_transformers": "sentence-transformers>=3.0.0",
    "pydantic": "pydantic>=2.0.0",
    "pydantic_settings": "pydantic-settings>=2.0.0",
}

IMPORT_MAP = {
    "dotenv": "dotenv",
    "sentence_transformers": "sentence_transformers",
    "pydantic_settings": "pydantic_settings",
}


def is_installed(module: str) -> bool:
    try:
        __import__(IMPORT_MAP.get(module, module))
        return True
    except ImportError:
        return False


def main() -> int:
    print(f"Python: {sys.executable}\n")
    missing = [spec for mod, spec in REQUIRED.items() if not is_installed(mod)]

    if not missing:
        print("All dependencies already installed.")
        return 0

    print("Missing packages:")
    for spec in missing:
        print(f"  - {spec}")

    print("\nInstalling missing packages only…")
    subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
