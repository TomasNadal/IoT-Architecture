from src.entrypoints.flask_app import app
from src.adapters.orm import start_mappers

if __name__ == "__main__":
    start_mappers()
    app.run(debug=True) 