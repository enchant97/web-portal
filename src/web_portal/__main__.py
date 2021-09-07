import os

from .main import create_app

if __name__ == "__main__":
    os.environ["QUART_ENV"] = "development"
    app = create_app()
    app.run()
