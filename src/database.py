import sqlite3
import datetime

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

        # Users table (Staff)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'agent',
                last_login TEXT
            )
        """)

        # Clients table (Pro CRM)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                passport_no TEXT UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                nationality TEXT,
                dob TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Bookings table (Pro Business Logic)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                service_type TEXT NOT NULL,
                destination TEXT NOT NULL,
                provider TEXT,
                start_date TEXT,
                end_date TEXT,
                total_cost REAL,
                selling_price REAL,
                status TEXT DEFAULT 'Pending',
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE CASCADE
            )
        """)

        # Payments table (Financials)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                booking_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_date TEXT DEFAULT CURRENT_TIMESTAMP,
                method TEXT,
                FOREIGN KEY (booking_id) REFERENCES bookings (id) ON DELETE CASCADE
            )
        """)

        conn.commit()
        conn.close()

    # --- User Management ---
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

    def update_last_login(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("UPDATE users SET last_login = ? WHERE username = ?", (now, username))
        conn.commit()
        conn.close()

    # --- Client Management ---
    def add_client(self, passport_no, first_name, last_name, phone, email, nationality, dob):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO clients (passport_no, first_name, last_name, phone, email, nationality, dob)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (passport_no, first_name, last_name, phone, email, nationality, dob))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def get_all_clients(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients ORDER BY last_name, first_name")
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
            WHERE first_name LIKE ? OR last_name LIKE ? OR passport_no LIKE ?
            ORDER BY last_name, first_name
        """, (wildcard, wildcard, wildcard))
        clients = cursor.fetchall()
        conn.close()
        return clients

    def update_client(self, client_id, passport_no, first_name, last_name, phone, email, nationality, dob):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE clients
                SET passport_no=?, first_name=?, last_name=?, phone=?, email=?, nationality=?, dob=?
                WHERE id=?
            """, (passport_no, first_name, last_name, phone, email, nationality, dob, client_id))
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

    # --- Booking Management ---
    def add_booking(self, client_id, service_type, destination, provider, start_date, end_date, total_cost, selling_price, status="Confirmed"):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bookings (client_id, service_type, destination, provider, start_date, end_date, total_cost, selling_price, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (client_id, service_type, destination, provider, start_date, end_date, total_cost, selling_price, status))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding booking: {e}")
            return False
        finally:
            conn.close()

    def get_all_bookings(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.*, c.first_name, c.last_name
            FROM bookings b
            JOIN clients c ON b.client_id = c.id
            ORDER BY b.start_date DESC
        """)
        bookings = cursor.fetchall()
        conn.close()
        return bookings

    def get_bookings_by_client(self, client_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bookings WHERE client_id = ? ORDER BY start_date DESC", (client_id,))
        bookings = cursor.fetchall()
        conn.close()
        return bookings

    def get_booking_by_id(self, booking_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT b.*, c.first_name, c.last_name, c.passport_no, c.email, c.phone
            FROM bookings b
            JOIN clients c ON b.client_id = c.id
            WHERE b.id = ?
        """, (booking_id,))
        booking = cursor.fetchone()
        conn.close()
        return booking

    # --- Financials & Stats ---
    def add_payment(self, booking_id, amount, method="Cash"):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO payments (booking_id, amount, method)
                VALUES (?, ?, ?)
            """, (booking_id, amount, method))
            conn.commit()
            return True
        except sqlite3.Error:
            return False
        finally:
            conn.close()

    def get_client_balance(self, client_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Total cost of all bookings for client
        cursor.execute("SELECT SUM(selling_price) FROM bookings WHERE client_id = ? AND status != 'Cancelled'", (client_id,))
        total_cost = cursor.fetchone()[0] or 0.0

        # Total payments made by client
        cursor.execute("""
            SELECT SUM(p.amount) FROM payments p
            JOIN bookings b ON p.booking_id = b.id
            WHERE b.client_id = ?
        """, (client_id,))
        total_paid = cursor.fetchone()[0] or 0.0

        conn.close()
        return total_cost - total_paid

    def get_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM clients")
        client_count = cursor.fetchone()[0]

        # Monthly Revenue (Current Month)
        current_month = datetime.datetime.now().strftime("%Y-%m")
        cursor.execute("""
            SELECT SUM(selling_price) FROM bookings
            WHERE status != 'Cancelled' AND strftime('%Y-%m', start_date) = ?
        """, (current_month,))
        revenue = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'Pending'")
        pending_bookings = cursor.fetchone()[0]

        conn.close()
        return {
            "total_clients": client_count,
            "monthly_revenue": revenue,
            "pending_bookings": pending_bookings
        }

    def get_monthly_revenue_stats(self, months=6):
        conn = self.get_connection()
        cursor = conn.cursor()

        stats = {}
        for i in range(months):
            date = datetime.datetime.now() - datetime.timedelta(days=30*i)
            month_str = date.strftime("%Y-%m")
            label = date.strftime("%b")

            cursor.execute("""
                SELECT SUM(selling_price) FROM bookings
                WHERE status != 'Cancelled' AND strftime('%Y-%m', start_date) = ?
            """, (month_str,))
            val = cursor.fetchone()[0] or 0.0
            stats[label] = val

        conn.close()
        # Return reversed to show chronological order
        return {"labels": list(reversed(list(stats.keys()))), "values": list(reversed(list(stats.values())))}
