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

    # Patch the 'connection' property of mysql to return our mock_connection
    with patch.object(type(mysql), "connection", new_callable=property(lambda self: mock_connection)):
        with app.test_client() as client:
            yield client


def test_homepage(client):
    """
    Test the '/' route for fetching messages.
    """
    mock_messages = [("Hello",), ("World",)]
    mysql.connection.cursor.return_value.fetchall.return_value = mock_messages

    response = client.get('/')
    assert response.status_code == 200
    assert b"Hello" in response.data or b"World" in response.data


def test_submit_message(client):
    """
    Test POST /submit route to insert new message.
    """
    response = client.post('/submit', data={'new_message': 'Test message'})
    assert response.status_code == 200
    assert response.is_json
    assert response.get_json()['message'] == 'Test message'

    mysql.connection.cursor.return_value.execute.assert_called_once_with(
        'INSERT INTO messages (message) VALUES (%s)', ['Test message']
    )
    mysql.connection.commit.assert_called_once()


def test_init_db():
    """
    Test init_db function to ensure table creation is called.
    """
    from app import init_db

    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    with patch.object(type(mysql), "connection", new_callable=property(lambda self: mock_connection)):
        init_db()

    mock_cursor.execute.assert_called_once()
    mock_connection.commit.assert_called_once()
