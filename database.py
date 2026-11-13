
import sqlite3
import os
from contextlib import contextmanager

# Location of our database
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_NAME = os.path.join(DATA_DIR, "afya_track.db")


@contextmanager
def get_connection():
    """Open and safely manage a database connection."""
    connection = None

    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        connection = sqlite3.connect(DB_NAME)
        connection.row_factory = sqlite3.Row
        yield connection
        connection.commit()

    except (sqlite3.Error, OSError):
        if connection:
            connection.rollback()
        raise

    finally:
        if connection:
            connection.close()


def init_db():
    """Create the clients table if it does not exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER,
                sex TEXT,
                residence TEXT,
                visit_count INTEGER DEFAULT 0,
                last_visit_date TEXT,
                last_activity TEXT,
                followup_date TEXT,
                followup_done INTEGER DEFAULT 0
            )
        """)


def add_client(name, age, sex, residence):
    """Register a new client."""
    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO clients (name, age, sex, residence)
            VALUES (?, ?, ?, ?)
        """, (name, age, sex, residence))

        return cursor.lastrowid


def get_all_clients():
    """Retrieve all registered clients."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM clients ORDER BY id DESC"
        ).fetchall()

        return [dict(row) for row in rows]


def get_client(client_id):
    """Retrieve one client using their ID."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM clients WHERE id = ?",
            (client_id,)
        ).fetchone()

        return dict(row) if row else None


def update_client(client_id, name, age, sex, residence):
    """Update an existing client's information."""
    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE clients
            SET name = ?, age = ?, sex = ?, residence = ?
            WHERE id = ?
        """, (name, age, sex, residence, client_id))

        return cursor.rowcount > 0


def delete_client(client_id):
    """Delete a client record."""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM clients WHERE id = ?",
            (client_id,)
        )

        return cursor.rowcount > 0


def record_visit(client_id, visit_date, activity):
    """Record a visit and update the client's visit count."""
    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE clients
            SET visit_count = visit_count + 1,
                last_visit_date = ?,
                last_activity = ?
            WHERE id = ?
        """, (visit_date, activity, client_id))

        return cursor.rowcount > 0


def schedule_followup(client_id, followup_date):
    """Set a follow-up date for a client."""
    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE clients
            SET followup_date = ?, followup_done = 0
            WHERE id = ?
        """, (followup_date, client_id))

        return cursor.rowcount > 0


def complete_followup(client_id):
    """Mark a client's follow-up as completed."""
    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE clients
            SET followup_done = 1
            WHERE id = ? AND followup_date IS NOT NULL
        """, (client_id,))

        return cursor.rowcount > 0


def get_overdue_clients(today):
    """Find clients with pending follow-ups before today's date."""
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM clients
            WHERE followup_date < ?
            AND followup_done = 0
            AND followup_date IS NOT NULL
            ORDER BY followup_date ASC
        """, (today,)).fetchall()

        return [dict(row) for row in rows]
