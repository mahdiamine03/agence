import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name="agency.db"):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'agent'
            )
        """)

        # Clients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                passport_number TEXT UNIQUE NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                notes TEXT
            )
        """)

        # Bookings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                destination TEXT NOT NULL,
                hotel TEXT,
                flight_details TEXT,
                travel_date TEXT,
                return_date TEXT,
                price REAL,
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    # User Management
    def add_user(self, username, password_hash, role='agent'):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                           (username, password_hash, role))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_user_by_username(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        return user

    # Client Management
    def add_client(self, full_name, passport_number, phone, email, address, notes):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clients (full_name, passport_number, phone, email, address, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (full_name, passport_number, phone, email, address, notes))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_all_clients(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients ORDER BY full_name")
        clients = cursor.fetchall()
        conn.close()
        return clients

    def get_client_by_id(self, client_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        client = cursor.fetchone()
        conn.close()
        return client

    def search_clients(self, query):
        conn = self.get_connection()
        cursor = conn.cursor()
        wildcard = f"%{query}%"
        cursor.execute("""
            SELECT * FROM clients
            WHERE full_name LIKE ? OR passport_number LIKE ?
            ORDER BY full_name
        """, (wildcard, wildcard))
        clients = cursor.fetchall()
        conn.close()
        return clients

    def update_client(self, client_id, full_name, passport_number, phone, email, address, notes):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clients
                SET full_name=?, passport_number=?, phone=?, email=?, address=?, notes=?
                WHERE id=?
            """, (full_name, passport_number, phone, email, address, notes, client_id))
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()

    def delete_client(self, client_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM clients WHERE id=?", (client_id,))
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()

    # Booking Management
    def add_booking(self, client_id, destination, hotel, flight_details, travel_date, return_date, price, status):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bookings (client_id, destination, hotel, flight_details, travel_date, return_date, price, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (client_id, destination, hotel, flight_details, travel_date, return_date, price, status))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding booking: {e}")
            return False
        finally:
            conn.close()

    def get_bookings_by_client(self, client_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE client_id = ? ORDER BY travel_date", (client_id,))
        bookings = cursor.fetchall()
        conn.close()
        return bookings

    def get_all_bookings(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Join to get client name if needed, but for now simple fetch
        cursor.execute("""
            SELECT b.*, c.full_name
            FROM bookings b
            JOIN clients c ON b.client_id = c.id
            ORDER BY b.travel_date
        """)
        bookings = cursor.fetchall()
        conn.close()
        return bookings

    def get_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clients")
        client_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM bookings WHERE status != 'Cancelled'")
        booking_count = cursor.fetchone()[0]

        conn.close()
        return {"clients": client_count, "bookings": booking_count}
