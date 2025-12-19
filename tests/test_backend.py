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
        conn.close()

    def test_user_registration_login(self):
        # Test registration
        self.auth.register_user("testuser", "password123")
        user = self.db.get_user_by_username("testuser")
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], "testuser")
        self.assertNotEqual(user['password_hash'], "password123") # Should be hashed

        # Test login
        logged_in_user = self.auth.login("testuser", "password123")
        self.assertIsNotNone(logged_in_user)
        self.assertEqual(logged_in_user['username'], "testuser")

        # Test bad login
        bad_user = self.auth.login("testuser", "wrongpass")
        self.assertIsNone(bad_user)

    def test_client_management(self):
        # Add client
        success = self.db.add_client("John Doe", "P123456", "555-1234", "john@example.com", "123 St", "VIP")
        self.assertTrue(success)

        # Get clients
        clients = self.db.get_all_clients()
        self.assertEqual(len(clients), 1)
        self.assertEqual(clients[0]['full_name'], "John Doe")

        # Get client by id
        client = self.db.get_client_by_id(clients[0]['id'])
        self.assertIsNotNone(client)
        self.assertEqual(client['full_name'], "John Doe")

        # Search client
        results = self.db.search_clients("Doe")
        self.assertEqual(len(results), 1)

        # Update client
        self.db.update_client(clients[0]['id'], "John Doe Updated", "P123456", "555-1234", "john@example.com", "123 St", "VIP")
        clients = self.db.get_all_clients()
        self.assertEqual(clients[0]['full_name'], "John Doe Updated")

        # Delete client
        self.db.delete_client(clients[0]['id'])
        clients = self.db.get_all_clients()
        self.assertEqual(len(clients), 0)

    def test_booking_management(self):
        self.db.add_client("Jane Doe", "P987654", "555-5678", "jane@example.com", "456 Ave", "")
        clients = self.db.get_all_clients()
        client_id = clients[0]['id']

        success = self.db.add_booking(client_id, "Paris", "Hilton", "AF123", "2023-10-10", "2023-10-20", 1500.0, "Paid")
        self.assertTrue(success)

        bookings = self.db.get_bookings_by_client(client_id)
        self.assertEqual(len(bookings), 1)
        self.assertEqual(bookings[0]['destination'], "Paris")

        stats = self.db.get_stats()
        self.assertEqual(stats['bookings'], 1)

if __name__ == '__main__':
    unittest.main()
