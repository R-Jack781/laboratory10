import psycopg2
from psycopg2 import sql
from tabulate import tabulate

DB_NAME = "bugtracker_db"
DB_USER = "user_bugtracker"
DB_PASS = "password_bugtracker"
DB_HOST = "localhost"
DB_PORT = "5432"

# Список таблиць для керування (від FK до PK, хоча TRUNCATE CASCADE це вирішує)
TABLE_NAMES = ["Bug_Fixes", "Errors", "Programmers"]


def connect_db():
    """Створює та повертає з'єднання з БД."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        print(f"Помилка підключення до БД: {e}") 
        return None

def execute_query(conn, query, params=None, fetch=False):
    """Виконує SQL запит і повертає результат, якщо потрібно."""
    if conn is None:
        return []
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                return cur.fetchall(), [desc[0] for desc in cur.description]
            conn.commit()
            return []
    except psycopg2.Error as e:
        print(f"Помилка виконання запиту:\n{query}\nПомилка: {e}")
        conn.rollback()
        return []


def truncate_all_tables(conn):
    """
    Очищує всі дані з таблиць та скидає лічильники SERIAL/PK.
    Зберігає структуру таблиць.
    """
    print("\n--- ОЧИЩЕННЯ ДАНИХ ТА СКІДАННЯ ЛІЧИЛЬНИКІВ (TRUNCATE) ---")
    
    # Об'єднуємо всі назви таблиць у рядок через кому
    tables_string = ", ".join(TABLE_NAMES)
    
    # Використовуємо TRUNCATE з RESTART IDENTITY та CASCADE
    query = f"TRUNCATE {tables_string} RESTART IDENTITY CASCADE;"
    
    execute_query(conn, query)
    
    print("Дані всіх таблиць очищено, лічильники скинуто.")


if __name__ == "__main__":
    conn = connect_db()

    if conn:
        try:
            truncate_all_tables(conn)
            
        finally:
            conn.close()
            print("\nЗ'єднання з БД закрито.")