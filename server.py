"""Local MCP server for querying corporate employee records via SQLite.
Communicates over stdio using the FastMCP framework.
"""

import re
import sqlite3
from pathlib import Path
from typing import Any
from fastmcp import FastMCP

DB_PATH = Path(__file__).parent / "employees.db"

# Initialize FastMCP instance
mcp = FastMCP(
    name="employee-db-assistant",
    instructions=(
        "You have read-only access to an internal Indian company database with 1,000 employees. "
        "Use describe_table to inspect column names and types, and execute_query to run SELECT queries. "
        "All salaries are in INR. Format amounts neatly in Lakhs (LPA) or Crores (Cr) when answering."
    ),
)


def get_db_connection() -> sqlite3.Connection:
    """Open a read-only SQLite connection."""
    if not DB_PATH.exists():
        raise FileNotFoundError(f"Database file not found at {DB_PATH}. Run seed_db.py first.")

    # URI mode with mode=ro enforces engine-level read-only access
    conn = sqlite3.connect(f"file:{DB_PATH.resolve().as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def list_tables() -> list[str]:
    """List all available user tables in the SQLite database."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
        )
        return [row["name"] for row in cur.fetchall()]
    finally:
        conn.close()


@mcp.tool()
def describe_table(table_name: str = "employees") -> dict[str, Any]:
    """Return schema details, column types, total row count, and sample records for a table."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        # Validate that the table actually exists
        cur.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name = ?;", (table_name,)
        )
        if not cur.fetchone():
            return {"error": f"Table '{table_name}' does not exist in the database."}

        cur.execute(f"PRAGMA table_info({table_name});")
        columns = [
            {
                "cid": row[0],
                "name": row[1],
                "type": row[2],
                "not_null": bool(row[3]),
                "default": row[4],
                "primary_key": bool(row[5]),
            }
            for row in cur.fetchall()
        ]

        cur.execute(f"SELECT COUNT(*) FROM {table_name};")
        total_rows = cur.fetchone()[0]

        cur.execute(f"SELECT * FROM {table_name} LIMIT 3;")
        sample_rows = [dict(row) for row in cur.fetchall()]

        return {
            "table": table_name,
            "total_rows": total_rows,
            "columns": columns,
            "sample_rows": sample_rows,
        }
    finally:
        conn.close()


@mcp.tool()
def execute_query(sql_query: str, max_rows: int = 100) -> dict[str, Any]:
    """Safely run a read-only SELECT query against the database.

    Args:
        sql_query: The SQL SELECT statement to execute.
        max_rows: Maximum rows to return (defaults to 100).
    """
    raw_query = sql_query.strip().rstrip(";")

    # Strip inline and block comments
    cleaned = re.sub(r"--.*?$|/\*.*?\*/", "", raw_query, flags=re.DOTALL | re.MULTILINE).strip()
    if not cleaned:
        return {"error": "Query cannot be empty."}

    # Disallow multiple semicolon-separated statements
    if ";" in cleaned:
        return {"error": "Multiple queries in a single call are not allowed."}

    # Query must start with SELECT or WITH
    first_token = cleaned.split()[0].upper()
    if first_token not in ("SELECT", "WITH"):
        return {"error": f"Only SELECT queries are allowed. Received: '{first_token}'."}

    # Block any mutation or administrative statements
    blocked_keywords = {
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "CREATE",
        "REPLACE", "ATTACH", "DETACH", "PRAGMA", "VACUUM", "TRUNCATE"
    }
    tokens = {t.upper() for t in re.findall(r"\b[A-Za-z_]+\b", cleaned)}
    matched_blocked = tokens.intersection(blocked_keywords)
    if matched_blocked:
        return {
            "error": f"Operation not permitted: '{', '.join(matched_blocked)}' is blocked in read-only mode."
        }

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(cleaned)

        rows = cur.fetchmany(max_rows + 1)
        columns = [desc[0] for desc in cur.description] if cur.description else []

        truncated = len(rows) > max_rows
        result_rows = rows[:max_rows]

        return {
            "query": sql_query,
            "columns": columns,
            "count": len(result_rows),
            "truncated": truncated,
            "rows": [dict(r) for r in result_rows],
        }
    except sqlite3.Error as err:
        return {"error": f"Database error: {err}"}
    finally:
        conn.close()


if __name__ == "__main__":
    mcp.run()
