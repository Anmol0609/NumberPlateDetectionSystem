import sqlite3

def read_database():
    try:
        # Connect to the database
        conn = sqlite3.connect('license_plates.db')
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        # Print data from each table
        for table in tables:
            table_name = table[0]
            print(f"\nTable: {table_name}")
            print("-" * 50)
            
            # Get all rows from the table
            cursor.execute(f"SELECT * FROM {table_name}")
            rows = cursor.fetchall()
            
            # Get column names
            column_names = [description[0] for description in cursor.description]
            print(" | ".join(column_names))
            print("-" * 50)
            
            # Print all rows
            for row in rows:
                print(" | ".join(map(str, row)))

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    read_database()