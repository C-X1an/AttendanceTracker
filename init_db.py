"""Create a local database with a newly chosen administrator password."""
import getpass
import os
import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash


def initialize_database(path, password):
    path = Path(path)
    if len(password) < 12:
        raise ValueError("Choose an administrator password of at least 12 characters.")
    descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    os.close(descriptor)
    with sqlite3.connect(path) as connection:
        connection.executescript(Path(__file__).with_name("schema.sql").read_text(encoding="utf-8"))
        connection.execute("INSERT INTO users VALUES (?, ?, ?, ?)", ("superadmin", "ADMIN", "ADMIN", generate_password_hash(password)))


if __name__ == "__main__":
    destination = Path(os.environ.get("ATTENDANCE_DATABASE", str(Path(__file__).with_name("database.db"))))
    if destination.exists():
        raise SystemExit("Database already exists; initialization will not overwrite it.")
    password = getpass.getpass("New local administrator password (12+ characters): ")
    if password != getpass.getpass("Confirm password: "):
        raise SystemExit("Passwords do not match.")
    initialize_database(destination, password)
    print("Local database initialized. Sign in as superadmin using your chosen password.")
