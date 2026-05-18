import pymysql
from pymysql.cursors import DictCursor

DB_CONFIG = {
    "host" : "localhost",
    "user" : "root",
    "password":"mypassword",
    "database":"library_db",
    "cursorclass":DictCursor
}

def get_connection():
    connection = pymysql.connect(**DB_CONFIG)
    return connection

def create_user(name, email, password, role):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
            INSERT INTO users(name, email, password, role)
            VALUES(%s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (name, email, password, role)
            )
            connection.commit()
            return cursor.lastrowid
        
    finally:
        connection.close()

def get_user_by_email(email):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT * FROM users WHERE email=%s"
            cursor.execute(query,(email,))
            return cursor.fetchone()
    finally:
        connection.close()

def get_user_by_id(user_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT * FROM users WHERE id=%s"
            cursor.execute(query,(user_id,))
            return cursor.fetchone()
    finally:
        connection.close()

def add_book(title, author, quantity):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = """
            INSERT INTO books(title, author, quantity)
            VALUES(%s, %s, %s)
            """
            cursor.execute(
                query,
                (title, author, quantity)
            )
            connection.commit()
            return cursor.lastrowid
    finally:
        connection.close()

def get_all_books():
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query="SELECT * FROM books"
            cursor.execute(query)
            return cursor.fetchall()
    finally:
        connection.close()

def get_book_by_id(book_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = "SELECT * FROM books WHERE id=%s"
            cursor.execute(query, (book_id,))
            return cursor.fetchone()
    finally:
        connection.close()

def delete_book(book_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            query = "DELETE FROM books WHERE id=%s"
            cursor.execute(query, (book_id,))
            connection.commit()
    finally:
        connection.close()

def issue_book(user_id, book_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            issue_query = """
                INSERT INTO issued_books(user_id, book_id)
                VALUES(%s, %s)
            """
            cursor.execute(issue_query, (user_id, book_id))

            update_query = """
                UPDATE books
                SET quantity = quantity - 1
                WHERE id=%s
            """
            cursor.execute(update_query, (book_id,))
            connection.commit()
            return cursor.lastrowid
    finally:
        connection.close()

def return_book(user_id, book_id):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            delete_query = """
                DELETE FROM issued_books
                WHERE user_id=%s AND book_id=%s
            """
            cursor.execute(delete_query, (user_id, book_id))

            update_query = """
                UPDATE books
                SET quantity = quantity + 1
                WHERE id=%s
            """
            cursor.execute(update_query, (book_id,))
            connection.commit()
    finally:
        connection.close()

def get_issued_books():
    connection=get_connection()
    try:
        with connection.cursor() as cursor:
            query = """ 
            SELECT ib.id as issue_id,
            u.id as user_id,
            u.name as user_name,
            b.id as book_id,
            b.title as book_title,
            b.author
            FROM issued_books ib
            JOIN users u ON  ib.user_id=u.id
            JOIN books b ON  ib.book_id=b.id
            """
            cursor.execute(query)
            return cursor.fetchall()
    finally:
        connection.close()
