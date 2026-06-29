"""Development entry point: `python run.py` (equivalent to `flask --app app run`)."""
from app import app

if __name__ == "__main__":
    app.run(
        host=app.config["HOST"],
        port=app.config["PORT"],
        debug=app.config["DEBUG"],
    )
