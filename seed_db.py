"""Seeds the local SQLite database with 1,000 realistic Indian employee records.
Includes roles, departments, locations, and compensation details.
"""

import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path
from faker import Faker

DB_PATH = Path(__file__).parent / "employees.db"

# Fixed seed so generation is deterministic
random.seed(42)
fake = Faker("en_IN")
Faker.seed(42)

# Major Indian tech and business locations
CITIES = [
    ("Bengaluru", "Karnataka"),
    ("Hyderabad", "Telangana"),
    ("Pune", "Maharashtra"),
    ("Mumbai", "Maharashtra"),
    ("Gurugram", "Haryana"),
    ("Noida", "Uttar Pradesh"),
    ("Chennai", "Tamil Nadu"),
    ("Delhi", "Delhi"),
    ("Kolkata", "West Bengal"),
    ("Ahmedabad", "Gujarat"),
    ("Kochi", "Kerala"),
]

# Department roles with realistic INR salary bands
DEPARTMENTS = {
    "Engineering": [
        ("Junior Software Engineer", 600000, 1000000),
        ("Software Engineer", 1100000, 1800000),
        ("Senior Software Engineer", 2200000, 3600000),
        ("Staff Software Engineer", 3800000, 5800000),
        ("Engineering Manager", 4500000, 7200000),
        ("Principal Engineer", 5500000, 8800000),
        ("Director of Engineering", 8500000, 13000000),
        ("VP of Engineering", 13000000, 19000000),
    ],
    "Product": [
        ("Associate Product Manager", 800000, 1400000),
        ("Product Manager", 1600000, 2800000),
        ("Senior Product Manager", 2800000, 4500000),
        ("Group Product Manager", 4600000, 6800000),
        ("Director of Product", 7500000, 11500000),
        ("VP of Product", 12000000, 17500000),
    ],
    "Data & AI": [
        ("Junior Data Analyst", 550000, 900000),
        ("Data Scientist", 1300000, 2200000),
        ("Senior Machine Learning Engineer", 2600000, 4200000),
        ("Lead AI Researcher", 4500000, 7500000),
        ("Head of AI", 8500000, 14000000),
    ],
    "Sales": [
        ("Business Development Associate", 400000, 650000),
        ("Account Executive", 800000, 1400000),
        ("Senior Account Executive", 1500000, 2400000),
        ("Regional Sales Manager", 2400000, 3800000),
        ("Director of Sales", 5500000, 8500000),
        ("VP of Sales", 9500000, 15000000),
    ],
    "Marketing": [
        ("Digital Marketing Executive", 420000, 700000),
        ("Brand Specialist", 750000, 1200000),
        ("Senior Marketing Manager", 1600000, 2600000),
        ("Growth Lead", 2400000, 3800000),
        ("Director of Marketing", 5000000, 8000000),
        ("Chief Marketing Officer", 10000000, 16000000),
    ],
    "Finance": [
        ("Financial Analyst", 600000, 1000000),
        ("Senior Financial Analyst", 1100000, 1800000),
        ("Finance Controller", 2200000, 3500000),
        ("Director of Finance", 5500000, 8500000),
        ("Chief Financial Officer", 12000000, 20000000),
    ],
    "Human Resources": [
        ("HR Executive", 400000, 650000),
        ("Talent Acquisition Specialist", 700000, 1200000),
        ("Senior HR Business Partner", 1400000, 2400000),
        ("Head of Talent Acquisition", 2800000, 4500000),
        ("Chief People Officer", 9000000, 15000000),
    ],
    "Customer Operations": [
        ("Support Associate", 350000, 550000),
        ("Customer Success Manager", 800000, 1300000),
        ("Operations Team Lead", 1200000, 1900000),
        ("Director of Customer Success", 4000000, 6500000),
    ],
    "Legal": [
        ("Legal Counsel", 1000000, 1800000),
        ("Senior Legal Counsel", 2200000, 3600000),
        ("General Counsel", 9000000, 16000000),
    ],
    "IT": [
        ("IT Support Engineer", 450000, 750000),
        ("DevOps Engineer", 1400000, 2400000),
        ("Security Analyst", 2000000, 3400000),
        ("Head of IT", 6000000, 9500000),
    ],
}

FIRST_NAMES = [
    "Aarav", "Aanya", "Aditi", "Aditya", "Akash", "Amit", "Ananya", "Aniket", "Ankita", "Ansh",
    "Arjun", "Deepak", "Divya", "Gaurav", "Harsh", "Isha", "Ishaan", "Karan", "Kavya", "Khushi",
    "Krishna", "Manish", "Meera", "Neha", "Nikhil", "Nisha", "Pooja", "Pranav", "Prashant", "Priya",
    "Rahul", "Rajesh", "Riya", "Rohan", "Rohit", "Sameer", "Sanjay", "Shreya", "Siddharth", "Sneha",
    "Suresh", "Suyash", "Tanvi", "Tarun", "Varun", "Vikram", "Vikas", "Vishal", "Yash", "Zoya",
    "Siddhesh", "Ranjit", "Swati", "Kavita", "Geeta", "Sunil", "Vivek", "Ashwin", "Shalini", "Manoj",
]

LAST_NAMES = [
    "Sharma", "Verma", "Patel", "Singh", "Yadav", "Gupta", "Reddy", "Nair", "Iyer", "Rao",
    "Chatterjee", "Banerjee", "Mukherjee", "Deshmukh", "Kulkarni", "Joshi", "Mehta", "Shah", "Malhotra", "Kapoor",
    "Chopra", "Bhat", "Shenoy", "Hegde", "Pillai", "Menon", "Chauhan", "Agarwal", "Mishra", "Pandey",
    "Saxena", "Bose", "Dutta", "Das", "Ghosh", "Patil", "Pawar", "Shinde", "Gowda", "Naidu",
]

STATUS_CHOICES = ["Active"] * 88 + ["On Leave"] * 4 + ["Resigned"] * 6 + ["Retired"] * 2


def get_random_date(start_year: int, end_year: int) -> str:
    """Generate a random ISO date between start_year and end_year."""
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    delta = end - start
    return (start + timedelta(days=random.randint(0, delta.days))).isoformat()


def generate_phone() -> str:
    """Generate a realistic Indian 10-digit mobile number."""
    prefix = random.choice(["98", "99", "97", "96", "95", "91", "88", "87", "80", "79"])
    suffix = "".join(str(random.randint(0, 9)) for _ in range(8))
    return f"+91-{prefix}{suffix[:4]}-{suffix[4:]}"


def main(total_records: int = 1000):
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE employees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        phone TEXT,
        department TEXT NOT NULL,
        job_title TEXT NOT NULL,
        salary INTEGER NOT NULL,
        bonus_percentage REAL NOT NULL,
        hire_date DATE NOT NULL,
        birth_date DATE NOT NULL,
        city TEXT NOT NULL,
        state TEXT NOT NULL,
        country TEXT NOT NULL,
        manager_id INTEGER,
        performance_score INTEGER NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (manager_id) REFERENCES employees(id)
    );
    """)

    # Indexes for frequently queried filters
    cur.execute("CREATE INDEX idx_emp_dept ON employees(department);")
    cur.execute("CREATE INDEX idx_emp_salary ON employees(salary);")
    cur.execute("CREATE INDEX idx_emp_hire_date ON employees(hire_date);")
    cur.execute("CREATE INDEX idx_emp_status ON employees(status);")

    used_emails = set()
    records = []
    department_managers = {dept: [] for dept in DEPARTMENTS}
    dept_names = list(DEPARTMENTS.keys())

    for emp_id in range(1, total_records + 1):
        dept = random.choice(dept_names)
        roles = DEPARTMENTS[dept]

        # Early IDs are leaders so they can act as managers
        if emp_id <= 35:
            role_title, min_sal, max_sal = random.choice(roles[max(0, len(roles) - 2):])
        else:
            role_title, min_sal, max_sal = random.choice(roles)

        # Round salary to nearest 50k
        salary = (random.randint(min_sal, max_sal) // 50000) * 50000
        bonus_pct = round(random.uniform(0.08, 0.30), 2)

        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)

        # Clean corporate email
        base_email = f"{first_name.lower()}.{last_name.lower()}@company.in"
        email = base_email
        counter = 1
        while email in used_emails:
            email = f"{first_name.lower()}.{last_name.lower()}{counter}@company.in"
            counter += 1
        used_emails.add(email)

        phone = generate_phone()
        city, state = random.choice(CITIES)

        # Hire date distribution: 2010 to 2026
        if emp_id <= 15:
            hire_date = get_random_date(2010, 2012)
        elif 16 <= emp_id <= 70:
            hire_date = get_random_date(2015, 2015)
        else:
            hire_date = get_random_date(2013, 2026)

        birth_date = get_random_date(1965, 2002)
        performance_score = random.choices([1, 2, 3, 4, 5], weights=[5, 15, 45, 25, 10])[0]
        status = random.choice(STATUS_CHOICES)

        # Assign manager
        managers_in_dept = department_managers[dept]
        if emp_id <= 35 or not managers_in_dept:
            manager_id = None
        else:
            manager_id = random.choice(managers_in_dept)

        # Track leadership for future reporting lines
        if any(w in role_title for w in ("Director", "VP", "Manager", "Chief", "Head")):
            department_managers[dept].append(emp_id)

        records.append((
            emp_id, first_name, last_name, email, phone, dept, role_title,
            salary, bonus_pct, hire_date, birth_date, city, state, "India",
            manager_id, performance_score, status,
        ))

    cur.executemany("""
    INSERT INTO employees (
        id, first_name, last_name, email, phone, department, job_title,
        salary, bonus_percentage, hire_date, birth_date, city, state,
        country, manager_id, performance_score, status
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, records)

    conn.commit()
    conn.close()
    print(f"Generated {len(records)} employee records into {DB_PATH.name}.")


if __name__ == "__main__":
    main()
