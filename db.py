import sqlite3

def get_db_connection():
    """Returns a database connection to SQLite"""
    conn = sqlite3.connect('database/database.db')
    conn.row_factory = sqlite3.Row  # this should allow accessing columns by name - Commented added by ReeceA, 25/02/2025 @ 00:24 GMT
    return conn
