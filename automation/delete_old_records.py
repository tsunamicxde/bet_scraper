import sqlite3

conn = sqlite3.connect('matches_data.db')
cursor = conn.cursor()


def delete_old_records():
    two_days_ago = "datetime('now', '-3 days', 'localtime')"
    try:
        cursor.execute(f"DELETE FROM matches_data WHERE date < {two_days_ago}")
        cursor.execute(f"DELETE FROM full_matches_data WHERE date < {two_days_ago}")
        conn.commit()
    except sqlite3.Error as e:
        print("Ошибка при удалении устаревших записей:", e)
        conn.rollback()
