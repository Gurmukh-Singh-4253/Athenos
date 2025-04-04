from sqlalchemy import create_engine, text, inspect
import pandas as pd

def explore_database_and_contents(db_uri, limit=5):
    """
    Explores the schema and displays the contents of tables in a database.

    Args:
        db_uri (str): The database URI (e.g., 'sqlite:///your_database.db').
        limit (int): The maximum number of rows to display from each table.
    """
    try:
        engine = create_engine(db_uri)
        inspector = inspect(engine)

        print(f"Exploring database: {db_uri}\n")

        table_names = inspector.get_table_names()
        if table_names:
            print("Tables and their contents (first {} rows):\n".format(limit))
            for table_name in table_names:
                print(f"--- Table: {table_name} ---")

                # Get column names for better display
                columns = inspector.get_columns(table_name)
                column_names = [column['name'] for column in columns]
                print(f"  Columns: {', '.join(column_names)}")

                # Fetch and display the first few rows using pandas for nice formatting
                try:
                    with engine.connect() as connection:
                        query = text(f"SELECT * FROM {table_name} LIMIT {limit}")
                        result = connection.execute(query)
                        df = pd.DataFrame(result.fetchall(), columns=result.keys())
                        if not df.empty:
                            print(df.to_string(index=False))
                        else:
                            print("  (No data in this table)")
                except Exception as e:
                    print(f"  Error fetching data for table '{table_name}': {e}")
                print()
        else:
            print("No tables found in this database.\n")

        view_names = inspector.get_view_names()
        if view_names:
            print("Views:")
            for view_name in view_names:
                print(f"- {view_name}")
            print()
        else:
            print("No views found in this database.\n")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace 'sqlite:///your_database.db' with the actual path to your database file
    database_file = 'sqlite:///database.db'
    explore_database_and_contents(database_file)
