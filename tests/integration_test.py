import unittest
import sqlite3
from flask import Flask, jsonify, request
from portfolio import app, get_current_price

class TestPortfolioIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up the Flask app for testing
        cls.client = app.test_client()
        cls.client.testing = True

        # Create an in-memory SQLite database for testing
        cls.conn = sqlite3.connect(":memory:")
        cls.conn.row_factory = sqlite3.Row
        cursor = cls.conn.cursor()
        cursor.execute('''
            CREATE TABLE portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                amount REAL NOT NULL,
                price REAL NOT NULL
            )
        ''')
        cls.conn.commit()

    @classmethod
    def tearDownClass(cls):
        # Clean up the database after the test
        cls.conn.close()

    def test_add_stock_and_fetch_price(self):
        # 1. Test adding a stock to the portfolio
        response = self.client.post('/portfolio', data=dict(
            name="AAPL",
            amount=50,
            price=145
        ))

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Add Stock", response.data)

        # 2. Test if the stock is correctly inserted into the database
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM portfolio WHERE name = 'AAPL'")
        stock = cursor.fetchone()

        self.assertIsNotNone(stock)
        self.assertEqual(stock['name'], "AAPL")
        self.assertEqual(stock['amount'], 50)
        self.assertEqual(stock['price'], 145)

        # 3. Test fetching the current price of AAPL using Alpha Vantage API
        current_price = get_current_price("AAPL")
        self.assertIsNotNone(current_price)
        self.assertIsInstance(current_price, float)

if __name__ == '__main__':
    unittest.main()