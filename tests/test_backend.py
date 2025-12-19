import unittest
import os
import sqlite3
from src.database import DatabaseManager
from src.auth import AuthManager

class TestBackend(unittest.TestCase):
    def setUp(self):
        self.test_db = "test_agency.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = DatabaseManager(self.test_db)
        self.auth = AuthManager(self.db)

    def tearDown(self):
        self.db.get_connection().close()
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_create_tables(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        self.assertIn('users', tables)
        self.assertIn('clients', tables)
        self.assertIn('bookings', tables)
        self.assertIn('payments', tables)
        conn.close()

    def test_client_management(self):
        # Add client
        success = self.db.add_client("P12345", "John", "Doe", "555-123", "j@d.com", "US", "1990-01-01")
        self.assertTrue(success)

        # Get clients
        clients = self.db.get_all_clients()
        self.assertEqual(len(clients), 1)
        self.assertEqual(clients[0]['first_name'], "John")

        # Search
        results = self.db.search_clients("Doe")
        self.assertEqual(len(results), 1)

        # Unique Passport check
        success = self.db.add_client("P12345", "Jane", "Doe", "555-456", "j@d.com", "US", "1992-01-01")
        self.assertFalse(success)

    def test_booking_and_payments(self):
        self.db.add_client("P999", "Alice", "Wonder", "555-999", "a@w.com", "UK", "1995-05-05")
        clients = self.db.get_all_clients()
        client_id = clients[0]['id']

        # Add Booking
        # Use current date to ensure it counts for monthly revenue test
        import datetime
        now = datetime.datetime.now().strftime("%Y-%m-%d")
        success = self.db.add_booking(client_id, "Flight", "London", "BA", now, "2023-12-10", 800.0, 1000.0)
        self.assertTrue(success)

        bookings = self.db.get_bookings_by_client(client_id)
        self.assertEqual(len(bookings), 1)
        booking_id = bookings[0]['id']

        # Check Balance (Should be 1000 owed)
        balance = self.db.get_client_balance(client_id)
        self.assertEqual(balance, 1000.0)

        # Add Payment
        self.db.add_payment(booking_id, 400.0, "Cash")

        # Check Balance (Should be 600 owed)
        balance = self.db.get_client_balance(client_id)
        self.assertEqual(balance, 600.0)

        # Stats
        stats = self.db.get_stats()
        self.assertEqual(stats['monthly_revenue'], 1000.0)

if __name__ == '__main__':
    unittest.main()
