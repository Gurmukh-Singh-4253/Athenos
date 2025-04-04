import os
from sqlalchemy import create_engine, text

# Define the absolute path to the database file
DB_PATH = "/home/gurmukh/Developer/Athenos/Flask/database.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Ensure the parent directory exists
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

def run_sql_file(filename):
    """Reads and executes an SQL file."""
    with open(filename, "r") as file:
        sql_script = file.read()

    # Execute the SQL script
    with engine.connect() as connection:
        with connection.begin():  # Ensures atomic execution
            for statement in sql_script.split(";"):
                statement = statement.strip()
                if statement:
                    connection.execute(text(statement))

    print(f"Executed {filename} successfully.")

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print(f"Database not found. Creating new database at {DB_PATH}...")

    run_sql_file("schema.sql")

