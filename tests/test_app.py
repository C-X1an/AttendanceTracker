import importlib
import sqlite3
import sys

import pytest

from init_db import initialize_database

PASSWORD = "fictional-local-test-password"


@pytest.fixture
def application(tmp_path, monkeypatch):
    database = tmp_path / "attendance.db"
    initialize_database(database, PASSWORD)
    monkeypatch.setenv("ATTENDANCE_DATABASE", str(database))
    monkeypatch.setenv("ATTENDANCE_SESSION_DIR", str(tmp_path / "sessions"))
    sys.modules.pop("app", None)
    module = importlib.import_module("app")
    module.app.config.update(TESTING=True)
    yield module
    sys.modules.pop("app", None)


def test_initialization_has_no_attendance_records(tmp_path):
    database = tmp_path / "new.db"
    initialize_database(database, PASSWORD)
    with sqlite3.connect(database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM attendance").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1
        assert connection.execute("SELECT hashed_password FROM users").fetchone()[0] != PASSWORD


def test_initialization_never_overwrites_existing_data(tmp_path):
    database = tmp_path / "existing.db"
    initialize_database(database, PASSWORD)
    original = database.read_bytes()
    with pytest.raises(FileExistsError):
        initialize_database(database, PASSWORD)
    assert database.read_bytes() == original


def test_short_administrator_password_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        initialize_database(tmp_path / "new.db", "short")
    assert not (tmp_path / "new.db").exists()


@pytest.mark.parametrize("credentials", [{}, {"username": "does-not-exist", "password": PASSWORD}, {"username": "superadmin", "password": "wrong"}])
def test_invalid_login_is_handled_without_server_error(application, credentials):
    client = application.app.test_client()
    response = client.post("/login", data=credentials, follow_redirects=True)
    assert response.status_code == 200
    with client.session_transaction() as session:
        assert "username" not in session


@pytest.mark.parametrize("path", ["/superadmin", "/attendance_report", "/user_dashboard"])
def test_anonymous_user_cannot_read_protected_pages(application, path):
    assert application.app.test_client().get(path).status_code == 302


def test_normal_role_cannot_read_administrator_page(application):
    client = application.app.test_client()
    with client.session_transaction() as session:
        session["username"] = "fictional-user"
        session["role"] = "user"
    assert client.get("/superadmin").status_code == 302


def test_administrator_login_and_logout(application):
    client = application.app.test_client()
    assert client.post("/login", data={"username": "superadmin", "password": PASSWORD}).status_code == 302
    assert client.get("/superadmin").status_code == 200
    assert client.get("/logout").status_code == 302
    assert client.get("/superadmin").status_code == 302
