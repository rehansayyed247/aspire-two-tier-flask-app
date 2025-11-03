import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock, patch
from app import app, mysql


@pytest.fixture
def client():
    """
    Flask test client fixture with mocked MySQL connection.
    """
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    # Patch mysql.connection at the instance level
    with patch.object(mysql, "connection", mock_connection):
        with app.test_client() as client:
            yield client


def test_homepage(client):
    """
    Test that homepage loads successfully.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome" in response.data or b"Home" in response.data


def test_submit_message(client):
    """
    Test form submission endpoint (POST /submit).
    """
    form_data = {"name": "Test User", "message": "Hello Flask!"}

    response = client.post("/submit", data=form_data, follow_redirects=True)
    assert response.status_code in (200, 302)

    # Check if mock DB cursor executed an insert
    mysql.connection.cursor.return_value.execute.assert_called()


def test_init_db():
    """
    Test init_db function to ensure table creation is called.
    """
    from app import init_db

    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    # Patch mysql.connection to mock DB operations
    with patch.object(mysql, "connection", mock_connection):
        init_db()

    mock_cursor.execute.assert_called()
    mock_connection.commit.assert_called()
