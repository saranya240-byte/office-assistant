from pathlib import Path
import sqlite3
from datetime import datetime


DB_PATH = Path(__file__).resolve().parent.parent / "data" / "memory.db"


def get_short_term_memory(messages: list[dict], limit: int = 10) -> list[dict]:
    """
    Return the most recent messages from the current conversation.
    """

    if not messages:
        return []

    return messages[-limit:]


def format_conversation(messages: list[dict]) -> str:
    """
    Convert conversation messages into text for agents.
    """

    if not messages:
        return ""

    lines = []

    for message in messages:
        role = message.get("role", "").capitalize()
        content = message.get("content", "").strip()

        if content:
            lines.append(f"{role}: {content}")

    return "\n".join(lines)


def _create_table(connection):
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    connection.commit()


def save_long_term_memory(
    employee_id: str,
    user_message: str,
    assistant_response: str,
):
    """
    Persist a complete user/assistant exchange.
    """

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    _create_table(connection)

    cursor = connection.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO conversations (
            employee_id,
            role,
            message,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            employee_id,
            "user",
            user_message,
            timestamp,
        ),
    )

    cursor.execute(
        """
        INSERT INTO conversations (
            employee_id,
            role,
            message,
            created_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            employee_id,
            "assistant",
            assistant_response,
            timestamp,
        ),
    )

    connection.commit()
    connection.close()


def get_long_term_memory(
    employee_id: str,
    limit: int = 10,
) -> list[dict]:
    """
    Retrieve previous conversation messages for an employee.
    """

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    _create_table(connection)

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT role, message, created_at
        FROM conversations
        WHERE employee_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (employee_id, limit),
    )

    rows = cursor.fetchall()

    connection.close()

    rows.reverse()

    return [
        {
            "role": row[0],
            "content": row[1],
            "created_at": row[2],
        }
        for row in rows
    ]