import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import MagicMock
from app import app, mysql




@pytest.fixture
def client(monkeypatch):
    """
    Flask test client fixture with mocked MySQL cursor and connection.
    """
    # Mock MySQL connection and cursor
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mysql.connection = mock_connection

    # Create test client
    with app.test_client() as client:
        yield client


def test_homepage(client):
    """
    Test the '/' route for fetching messages.
    """
    # Mock fetchall return
    mock_messages = [("Hello",), ("World",)]
    mysql.connection.cursor.return_value.fetchall.return_value = mock_messages

    response = client.get('/')
    assert response.status_code == 200
    # The rendered page should contain at least one message
    assert b"Hello" in response.data or b"World" in response.data


def test_submit_message(client):
    """
    Test POST /submit route to insert new message.
    """
    response = client.post('/submit', data={'new_message': 'Test message'})
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()['message'] == 'Test message'

    # Verify MySQL insert was called correctly
    mysql.connection.cursor.return_value.execute.assert_called_once_with(
        'INSERT INTO messages (message) VALUES (%s)', ['Test message']
    )
    mysql.connection.commit.assert_called_once()


def test_init_db(monkeypatch):
    """
    Test init_db function to ensure table creation is called.
    """
    from app import init_db

    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mysql.connection = mock_connection

    init_db()

    mock_cursor.execute.assert_called_once()
    mysql.connection.commit.assert_called_once()
