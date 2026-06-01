from flask_migrate import Migrate

from app.config.database import db #type: ignore[import]
from app import create_app



app = create_app()
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(
        host = "0.0.0.0",
        port=5000,
        debug=True)