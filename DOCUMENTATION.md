# Employee Database MCP Server — Technical Documentation

A local Model Context Protocol (MCP) server providing LLMs (ChatGPT Desktop, Claude Desktop, Cursor) with safe, read-only SQL access to an internal SQLite database of 1,000 Indian corporate employee records.

---

## 1. Quickstart (Under 60 Seconds)

```powershell
# 1. Clone & enter directory
cd C:\Users\suyas\Downloads\mcp-test

# 2. Seed database (generates 1,000 Indian employee records)
uv run seed_db.py

# 3. Start MCP Server (stdio mode)
uv run server.py
```

---

## 2. End-to-End Flow & Lifecycle

```
[1. User Prompt]
       │  "Who has the highest salary in our company?"
       ▼
[2. ChatGPT Desktop]
       │  • Introspects schema via describe_table("employees")
       │  • Translates plain English into a SQL query:
       │    "SELECT first_name, last_name, job_title, department, salary 
       │     FROM employees ORDER BY salary DESC LIMIT 1"
       ▼ (stdio JSON-RPC call)
[3. MCP Server (server.py) — Security & Guardrail Check]
       │  ✔ Check 1: Must begin with SELECT or WITH
       │  ✔ Check 2: Reject multiple statements (no stacked ";" injection)
       │  ✔ Check 3: Keyword blacklist (rejects DROP, DELETE, INSERT, UPDATE, ALTER, etc.)
       │  ✔ Check 4: Enforce max_rows limit (default 100) to prevent token overflow
       │  ✔ Check 5: Engine-level read-only mount (?mode=ro) blocks any write attempts
       ▼ (if all checks pass)
[4. SQLite Database (employees.db)]
       │  Executes query against 1,000 indexed records
       ▼
[5. Structured Result returned to Server]
       │  JSON: [{"first_name": "Shreya", "last_name": "Naidu", "salary": 19600000, ...}]
       ▼ (stdio JSON-RPC response)
[6. ChatGPT Synthesizes Final Answer]
       │  "Shreya Naidu, Chief Financial Officer in Finance, has the highest salary 
       │   at ₹1.96 Crore (₹19,600,000) per year."
       ▼
[7. User Receives Clean, Direct Answer]
```

### Detailed Breakdown of the Steps:

1. **User asks in plain language**: The user submits a natural language question (e.g., *"Who joined in 2015?"*, *"Highest earner in Bengaluru?"*).
2. **Schema Introspection**: ChatGPT uses `describe_table("employees")` to inspect column names, types, and sample data. It understands that salaries are in `salary`, locations in `city`, dates in `hire_date`, etc.
3. **NL-to-SQL Translation**: ChatGPT formulates an optimized read-only ANSI SQL `SELECT` query tailored to answer the specific question.
4. **Server Guardrails Validation**: Before any query touches the database, `server.py` runs strict security checks:
   - **Syntax verification**: Ensures the query starts with `SELECT` or `WITH`.
   - **Injection defense**: Blocks semicolons containing multiple queries (`SELECT 1; DROP TABLE...`).
   - **Keyword blacklist**: Rejects mutating words like `DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`, `CREATE`, `REPLACE`, `ATTACH`, `PRAGMA`.
   - **Filesystem immutability**: SQLite connection uses `file:employees.db?mode=ro`, so the operating system itself rejects any write attempts.
   - **Row capping**: Limits responses to 100 rows to protect token limits.
5. **Execution & Data Return**: The query runs against `employees.db` and returns a clean, structured JSON payload over standard I/O (`stdio`).
6. **AI Formatting**: ChatGPT receives the data, formats the numbers into Indian Rupee units (LPA / Crores), and replies with a human-friendly answer.

---

## 3. Database Schema (`employees.db`)

The `employees` table contains 1,000 records across 10 departments and 11 Indian tech hubs (Bengaluru, Hyderabad, Pune, Mumbai, Gurgaon, Noida, etc.).

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | INTEGER | Primary Key (1 to 1000) |
| `first_name`, `last_name` | TEXT | Indian names (*Aarav Sharma, Shreya Naidu, etc.*) |
| `email` | TEXT | Corporate email (`firstname.lastname@company.in`) |
| `phone` | TEXT | Mobile number (`+91-98XXX-XXXXX`) |
| `department` | TEXT | Engineering, Product, Data & AI, Sales, Marketing, Finance, HR, Operations, Legal, IT |
| `job_title` | TEXT | Role hierarchy (Junior, Senior, Lead, Manager, Director, VP, CXO) |
| `salary` | INTEGER | Annual salary in INR (₹4,00,000 to ₹1,96,00,000) |
| `bonus_percentage` | REAL | Bonus multiplier (0.08 to 0.30) |
| `hire_date` | DATE | Hire date from 2010 to 2026 (ISO format `YYYY-MM-DD`) |
| `birth_date` | DATE | Employee birth date |
| `city`, `state`, `country` | TEXT | Indian cities, states, and "India" |
| `manager_id` | INTEGER | Self-referential Foreign Key to `employees.id` |
| `performance_score` | INTEGER | Rating from 1 to 5 |
| `status` | TEXT | `Active`, `On Leave`, `Resigned`, `Retired` |

---

## 4. MCP Tools Implemented

| Tool Name | Parameters | Purpose |
| :--- | :--- | :--- |
| `list_tables()` | None | Returns list of database tables (`["employees"]`). |
| `describe_table()` | `table_name: str` | Returns column names, types, primary keys, record count, and 3 sample rows. |
| `execute_query()` | `sql_query: str`, `max_rows: int = 100` | Safely executes a read-only `SELECT` query and returns structured results. |

---

## 5. Security & Guardrails

To prevent SQL injection and accidental database modification:
1. **Engine-Level Read-Only**: The SQLite connection string uses `file:employees.db?mode=ro`. The database file cannot be modified by any query.
2. **Statement Whitelisting**: Queries must begin with `SELECT` or `WITH`.
3. **Keyword Blacklist**: Statements containing `DROP`, `DELETE`, `INSERT`, `UPDATE`, `ALTER`, `CREATE`, `REPLACE`, `ATTACH`, or `PRAGMA` are rejected.
4. **Single Statement Check**: Semicolons followed by additional commands are blocked to prevent stacked SQL injection.
5. **Row Capping**: Responses are limited to 100 rows by default to prevent context window overflow.

---

## 6. ChatGPT Desktop Configuration

Add this server in **ChatGPT Desktop** > **Settings** > **Developer** > **MCP Servers**:

- **Name**: `employee`
- **Type**: `STDIO`
- **Command**: `C:\Users\suyas\AppData\Local\hermes\bin\uv.exe` *(or simply `uv`)*
- **Arguments**:
  - `run`
  - `server.py`
- **Working directory**: `C:\Users\suyas\Downloads\mcp-test`

*Note: In Claude Desktop, save this snippet into `%APPDATA%\Claude\claude_desktop_config.json`.*

---

## 7. Sample Questions & Verified Outputs

| Question | SQL Generated by AI | Expected Result |
| :--- | :--- | :--- |
| *"Who has the highest salary?"* | `SELECT * FROM employees ORDER BY salary DESC LIMIT 1;` | **Shreya Naidu**, CFO (Finance), **₹1.96 Crore** (₹19,600,000) |
| *"Who joined in 2015?"* | `SELECT * FROM employees WHERE strftime('%Y', hire_date) = '2015';` | Returns 2015 cohort (*Tanvi Shinde, Sanjay Reddy, etc.*) |
| *"Who is the longest serving active employee?"* | `SELECT * FROM employees WHERE status='Active' ORDER BY hire_date ASC LIMIT 1;` | **Prashant Iyer**, Director of Product (Hired: **2010-01-31**) |
| *"Average salary by department?"* | `SELECT department, ROUND(AVG(salary), 2) FROM employees GROUP BY department;` | Clean table breakdown in INR |

---

## 8. Common Gotchas & Fixes

1. **ChatGPT answers conversationally instead of running tool**:
   - Ensure you are in Developer / Work with Apps mode with the tool enabled. Start a **`+ New Chat`** so the session loads the active tool definition.
2. **Terminal character encoding error on Windows**:
   - Windows PowerShell defaults to `cp1252`. Console logs use ASCII (`INR`, `[OK]`) rather than unicode symbols (`₹`, `✓`) to ensure portability.
3. **Database changes not reflecting in chat**:
   - Start a **`+ New Chat`** in ChatGPT to reset previous conversation memory and query the updated SQLite database fresh.

---

## 9. Project Files Overview

- [server.py](file:///c:/Users/suyas/Downloads/mcp-test/server.py): FastMCP server implementation with query safety guardrails.
- [seed_db.py](file:///c:/Users/suyas/Downloads/mcp-test/seed_db.py): Generates 1,000 Indian corporate records using Faker.
- [pyproject.toml](file:///c:/Users/suyas/Downloads/mcp-test/pyproject.toml): Project dependencies (`fastmcp`, `faker`).
- [employees.db](file:///c:/Users/suyas/Downloads/mcp-test/employees.db): Generated SQLite database.
