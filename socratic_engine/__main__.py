import os
from .socratic_engine import repl


def main():
    backend_url = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
    repl(backend_url)


if __name__ == "__main__":
    main()
