"""
This file is for experiment purposes only.
This is for removing the entire database, to create another new, fresh database (in case some data are corrupted, because this happens occasionally).
"""

import sqlite3

def clear_diary_table():
    try:
        # Connect to your database
        conn = sqlite3.connect("wellbeing.db")
        cursor = conn.cursor()

        # Delete all rows from the diary table
        cursor.execute("DELETE FROM diary")

        # Commit changes
        conn.commit()
        print("All entries in the diary table have been deleted.")

    except Exception as e:
        print(f"Error while clearing diary table: {e}")

    finally:
        # Close connection
        conn.close()

# Run the function
if __name__ == "__main__":
    clear_diary_table()