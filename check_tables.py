import sqlite3


def check_tables():
    conn = sqlite3.connect("data/jobpilot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("All tables:", [table[0] for table in tables])

    # Check record counts for each table
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        count = cursor.fetchone()[0]
        print(f"  {table_name}: {count} records")

    conn.close()


if __name__ == "__main__":
    check_tables()
