# 🏢 Local SQLite Employee MCP Server (Indian Enterprise Edition)

A production-ready Model Context Protocol (MCP) server built with **Python FastMCP** and **SQLite**, designed to enable AI assistants like **ChatGPT Desktop**, **Claude Desktop**, and **Cursor** to query internal corporate employee data safely.

> 📖 **Full in-depth walkthrough**: Check out [DOCUMENTATION.md](file:///c:/Users/suyas/Downloads/mcp-test/DOCUMENTATION.md) for detailed architecture, design rationales, troubleshooting gotchas, and sample prompt queries!

---

## 🌟 Highlights
- **1,000 Realistic Indian Employees**: Pre-populated database with 17 corporate columns (Indian names, tech hubs like Bengaluru, Pune, Hyderabad, Gurgaon, INR ₹ salaries in LPA/Crores, roles, hire dates, managers, performance ratings, and status).
- **Safe Read-Only SQL Engine**:
  - `list_tables`: Discovers available tables.
  - `describe_table`: Returns columns, data types, row count, and sample records.
  - `execute_query`: Executes any custom read-only `SELECT` query.
- **Enterprise-Grade Security**:
  - SQLite database is mounted in strictly read-only mode (`?mode=ro`).
  - AST / regex validation blocks all mutations (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, etc.).
  - Protects against multi-statement query injections.
  - Caps maximum return rows to prevent token exhaustion.

---

## 📂 Project Structure
```
mcp-test/
├── employees.db         # SQLite database containing 1,000 Indian corporate employee records
├── seed_db.py           # Script to generate realistic mock data with Faker (en_IN)
├── server.py            # FastMCP server implementation (stdio transport)
├── pyproject.toml       # Modern uv project definition & dependencies
├── DOCUMENTATION.md     # Technical documentation & guide
└── README.md            # Quickstart guide
```

---

## ⚡ Quickstart

### 1. Requirements
Ensure you have `uv` installed. If not, install it via PowerShell:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Seed Database
```powershell
# Seed database with 1,000 Indian corporate records
uv run seed_db.py
```

---

## 🤖 Connecting to ChatGPT Desktop

1. In **ChatGPT Desktop**, open **Settings** -> **Developer** (or **Work with Apps** / **MCP Servers**).
2. Click **Add Server**:
   - **Name**: `employee`
   - **Type**: `STDIO`
   - **Command to launch**: `C:\Users\suyas\AppData\Local\hermes\bin\uv.exe` *(or simply `uv`)*
   - **Arguments**:
     - `run`
     - `server.py`
   - **Working directory**: `C:\Users\suyas\Downloads\mcp-test`
3. Click **Save**.
4. Open a **`+ New Chat`**, look for the tool icon, and start asking questions!

---

## 💬 Sample Questions to Try
- *"Who has the highest salary in our company and what is their role and city?"*
- *"Which employees joined the company in 2015?"*
- *"Who is the longest-serving active employee?"*
- *"What is the average salary broken down by department?"*
- *"Show me all employees based in Bengaluru with a performance rating of 5."*
