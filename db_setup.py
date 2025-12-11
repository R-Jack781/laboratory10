import psycopg2
from psycopg2 import sql
from tabulate import tabulate
import os

# --- КОНФІГУРАЦІЯ БД ---
DB_NAME = "bugtracker_db"
DB_USER = "user_bugtracker"
DB_PASS = "password_bugtracker"
DB_HOST = "localhost" 
DB_PORT = "5432"

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
        return ([], []) if fetch else []
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if fetch:
                if cur.description is not None:
                    return cur.fetchall(), [desc[0] for desc in cur.description]
                else:
                    return [], []
            conn.commit()
            return []
    except psycopg2.Error as e:
        # Виведення помилки бази даних у функції execute_query
        print(f"Помилка виконання запиту:\n{query}\nПомилка: {e}")
        conn.rollback()
        return ([], []) if fetch else []


def create_tables(conn):
    """Створює необхідні таблиці з обмеженнями."""
    print("Створення таблиць...")

    # Видаляємо старі таблиці для чистого старту та коректного створення нових FK
    drop_tables = """
    DROP TABLE IF EXISTS Bug_Fixes CASCADE;
    DROP TABLE IF EXISTS Errors CASCADE;
    DROP TABLE IF EXISTS Programmers CASCADE;
    """
    execute_query(conn, drop_tables)

    # 1. Таблиця Programmers (Використовуємо 'id' як PK для сумісності)
    programisty_table = """
    CREATE TABLE IF NOT EXISTS Programmers (
        id SERIAL PRIMARY KEY,
        surname VARCHAR(50) NOT NULL,
        first_name VARCHAR(50) NOT NULL,
        phone VARCHAR(15) UNIQUE
    );
    """

    # 2. Таблиця Errors (Використовуємо 'id' як PK для сумісності)
    errors_table = """
    CREATE TABLE IF NOT EXISTS Errors (
        id SERIAL PRIMARY KEY,
        error_description TEXT NOT NULL,
        date_received DATE NOT NULL,
        error_level VARCHAR(10) NOT NULL CHECK (error_level IN ('critical', 'important', 'minor')),
        category VARCHAR(50) NOT NULL CHECK (category IN ('interface', 'data', 'calculation algorithm', 'other', 'unknown category')),
        source VARCHAR(20) NOT NULL CHECK (source IN ('user', 'tester'))
    );
    """

    # 3. Таблиця Bug_Fixes (FK тепер називаються *id)
    fixes_table = """
    CREATE TABLE IF NOT EXISTS Bug_Fixes (
        id SERIAL PRIMARY KEY,
        error_id INTEGER NOT NULL REFERENCES Errors(id) ON DELETE CASCADE,
        programmer_id INTEGER NOT NULL REFERENCES Programmers(id) ON DELETE RESTRICT,
        start_date DATE NOT NULL,
        duration_days INTEGER NOT NULL CHECK (duration_days IN (1, 2, 3)),
        cost_per_day NUMERIC(10, 2) NOT NULL
    );
    """

    execute_query(conn, programisty_table)
    execute_query(conn, errors_table)
    execute_query(conn, fixes_table)
    print("Таблиці успішно створені.")

def insert_data(conn):
    """Заповнює таблиці мінімально необхідним обсягом даних."""
    print("Заповнення таблиць даними...")

    prog_data = [
        ('Коваль', 'Іван', '(050) 123-4567'),
        ('Мельник', 'Олена', '(067) 987-6543'),
        ('Шевченко', 'Петро', '(093) 111-2233'),
        ('Лисенко', 'Марія', '(099) 444-5566'),
    ]
    for p in prog_data:
        execute_query(conn, 
                      "INSERT INTO Programmers (surname, first_name, phone) VALUES (%s, %s, %s);", 
                      (p[0], p[1], p[2]))

    errors_data = [
        ('Форма входу не валідує електронну пошту', '2025-11-01', 'critical', 'interface', 'user'),
        ('Некоректний розрахунок ПДВ', '2025-11-02', 'critical', 'calculation algorithm', 'tester'),
        ('Поле "Дата" приймає невірний формат', '2025-11-03', 'important', 'data', 'user'),
        ('Застарілий логотип на головній сторінці', '2025-11-04', 'minor', 'interface', 'tester'),
        ('Повільне завантаження сторінки з понад 1000 записів', '2025-11-05', 'important', 'data', 'user'),
        ('Критичний збій при збереженні (SQL ін’єкція)', '2025-11-06', 'critical', 'data', 'tester'),
        ('Неправильна назва кнопки', '2025-11-07', 'minor', 'interface', 'user'),
        ('Множення на 0 призводить до помилки замість 0', '2025-11-08', 'critical', 'calculation algorithm', 'tester'),
        ('Посилання веде на сторінку 404', '2025-11-09', 'important', 'other', 'user'),
        ('Некоректна обробка порожніх полів', '2025-11-10', 'important', 'data', 'tester'),
        ('Неправильний відступ у мобільній версії', '2025-11-11', 'minor', 'interface', 'user'),
        ('Невірний перерахунок при зміні валюти', '2025-11-12', 'critical', 'calculation algorithm', 'tester'),
        ('Система зависає під час експорту даних', '2025-11-13', 'critical', 'other', 'user'),
        ('Дрібна орфографічна помилка', '2025-11-14', 'minor', 'other', 'tester'),
        ('Невірна фільтрація за датою', '2025-11-15', 'important', 'data', 'user'),
        ('Відсутній прапорець для згоди', '2025-11-16', 'important', 'interface', 'tester'),
        ('Немає відображення помилки при невдалій транзакції', '2025-11-17', 'critical', 'unknown category', 'user'),
        ('Завищення ціни при застосуванні знижки', '2025-11-18', 'critical', 'calculation algorithm', 'tester'),
        ('Некоректне обрізання довгих текстових полів', '2025-11-19', 'minor', 'interface', 'user'),
        ('Не враховується додатковий відсоток', '2025-11-20', 'important', 'calculation algorithm', 'tester'),
    ]
    for p in errors_data:
        execute_query(conn, 
                      "INSERT INTO Errors (error_description, date_received, error_level, category, source) VALUES (%s, %s, %s, %s, %s);",
                      p)

    fixes_data = [
        # (error_id, programmer_id, start_date, duration_days, cost_per_day)
        (1, 1, '2025-11-01', 3, 1000.00), (2, 2, '2025-11-03', 2, 1200.00), (3, 3, '2025-11-04', 1, 900.00), (4, 4, '2025-11-05', 1, 1100.00), 
        (5, 1, '2025-11-06', 2, 1000.00), (6, 2, '2025-11-07', 3, 1200.00), (7, 3, '2025-11-08', 1, 900.00), (8, 4, '2025-11-09', 3, 1100.00), 
        (9, 1, '2025-11-10', 2, 1000.00), (10, 2, '2025-11-11', 1, 1200.00), (11, 3, '2025-11-12', 1, 900.00), (12, 4, '2025-11-13', 2, 1100.00),
        (13, 1, '2025-11-14', 3, 1000.00), (14, 2, '2025-11-15', 1, 1200.00), (15, 3, '2025-11-16', 2, 900.00), (16, 4, '2025-11-17', 1, 1100.00),
        (17, 1, '2025-11-18', 3, 1000.00), (18, 2, '2025-11-19', 2, 1200.00), (19, 3, '2025-11-20', 1, 900.00), (20, 4, '2025-11-21', 2, 1100.00),
    ]
    
    # ФІНАЛЬНЕ ВИПРАВЛЕННЯ: Використовуємо error_id та programmer_id для вставки
    for v in fixes_data:
        execute_query(conn, 
                      "INSERT INTO Bug_Fixes (error_id, programmer_id, start_date, duration_days, cost_per_day) VALUES (%s, %s, %s, %s, %s);", 
                      v)
    print("Дані успішно заповнені.")

def display_table(conn, table_name):
    """Виводить структуру та дані таблиці в консоль."""
    print(f"\n--- Таблиця: {table_name} ---")
    try:
        data, headers = execute_query(conn, f"SELECT * FROM {table_name};", fetch=True)
        if data:
            print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
        else:
            print("Таблиця порожня або не вдалося отримати дані.")
    except Exception as e:
        print(f"Помилка при виведенні таблиці {table_name}: {e}")

def display_query_result(conn, title, query, params=None):
    """Виконує запит і виводить результат в консоль."""
    print(f"\n--- Запит: {title} ---")
    try:
        data, headers = execute_query(conn, query, params, fetch=True)
        if data:
            print(tabulate(data, headers=headers, tablefmt="fancy_grid"))
        else:
            print("Результатів немає або не вдалося отримати дані.")
    except Exception as e:
        print(f"Помилка при виконанні запиту '{title}': {e}")


def run_queries(conn):
    """Виконує всі необхідні за завданням запити, використовуючи адаптовані імена стовпців."""
    print("\n\n#################################################")
    print("### ВИКОНАННЯ ЗАПИТІВ ###")
    print("#################################################")

    # 1. Відобразити всі критичні помилки. Відсортувати по коду помилки.
    q1 = """
    SELECT * FROM Errors 
    WHERE error_level = 'critical' 
    ORDER BY id; -- Адаптовано до фактичного PK
    """
    display_query_result(conn, "Всі критичні помилки (Сортування по коду)", q1)

    # 2. Порахувати кількість помилок кожного рівня (підсумковий запит).
    q2 = """
    SELECT 
        error_level, 
        COUNT(id) AS Error_Count -- Адаптовано до фактичного PK
    FROM Errors
    GROUP BY error_level;
    """
    display_query_result(conn, "Кількість помилок кожного рівня (Підсумковий)", q2)

    # 3. Порахувати вартість роботи програміста при виправленні кожної помилки (запит з обчислювальним полем).
    q3 = """
    SELECT 
        id AS fix_code, -- Адаптовано до фактичного PK
        error_id, -- Адаптовано до фактичного FK
        duration_days, 
        cost_per_day,
        (duration_days * cost_per_day) AS Total_Work_Cost
    FROM Bug_Fixes;
    """
    display_query_result(conn, "Вартість роботи при виправленні помилки (Обчислювальне поле)", q3)

    param_source = 'user'
    # 4. Помилки, що надійшли із заданого джерела (запит з параметром)
    q4 = """
    SELECT * FROM Errors 
    WHERE source = %s;
    """
    display_query_result(conn, f"Помилки, що надійшли від джерела: '{param_source}' (Запит з параметром)", q4, (param_source,))

    # 5. Кількість помилок за джерелом (Підсумковий)
    q5 = """
    SELECT 
        source, 
        COUNT(id) AS Error_Count -- Адаптовано до фактичного PK
    FROM Errors
    WHERE source IN ('user', 'tester')
    GROUP BY source;
    """
    display_query_result(conn, "Кількість помилок за джерелом (Підсумковий)", q5)

    # 6. Перехресний запит (використовуємо ID та *_id)
    q6 = """
    SELECT
        p.surname,
        SUM(CASE WHEN e.error_level = 'critical' THEN 1 ELSE 0 END) AS Critical,
        SUM(CASE WHEN e.error_level = 'important' THEN 1 ELSE 0 END) AS Important,
        SUM(CASE WHEN e.error_level = 'minor' THEN 1 ELSE 0 END) AS Minor,
        COUNT(b.id) AS Total_Fixed -- Адаптовано до фактичного PK
    FROM Programmers p
    JOIN Bug_Fixes b ON p.id = b.programmer_id -- Адаптовано: p.id та b.programmer_id
    JOIN Errors e ON b.error_id = e.id        -- Адаптовано: b.error_id та e.id
    GROUP BY p.surname
    ORDER BY p.surname;
    """
    display_query_result(conn, "Кількість помилок за рівнем, виправлених кожним програмістом (Перехресний/Умовна агрегація)", q6)


if __name__ == "__main__":
    conn = connect_db()

    if conn:
        try:
            # 1. Створення таблиць (виконує DROP/CREATE, адаптовано до id/*_id)
            create_tables(conn)

            # 2. Вставка даних (використовує error_id, programmer_id)
            insert_data(conn)

            print("\n\n#################################################")
            print("### ВИВЕДЕННЯ ВСІХ ТАБЛИЦЬ ###")
            print("#################################################")
            display_table(conn, "Programmers")
            display_table(conn, "Errors")
            display_table(conn, "Bug_Fixes")

            run_queries(conn)
            
        finally:
            conn.close()
            print("\nЗ'єднання з БД закрито.")