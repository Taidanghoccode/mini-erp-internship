import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.db.db import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    print("🔥 Dropping schema public...")
    db.session.execute(text("DROP SCHEMA public CASCADE;"))

    print("🧱 Creating schema public...")
    db.session.execute(text("CREATE SCHEMA public;"))

    db.session.commit()
    print("✅ SCHEMA has been fully reset!")
