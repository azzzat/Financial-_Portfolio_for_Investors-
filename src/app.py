from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import requests

app = Flask(__name__, template_folder='./templates')

# Alpha Vantage API Key
API_KEY = "QKTQZFPRS4K252MM"

# Database setup
def create_table():
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            price REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

create_table()

# Helper function to get current stock price
mock_data = {
    'NVDA': {
        "Global Quote": {
            "05. price": "500.00"  # Цена для NVDA
        }
    },
    'GOOG': {
        "Global Quote": {
            "05. price": "2800.00"  # Цена для GOOG
        }
    }
}

def get_current_price(symbol):

    if symbol in mock_data:
            response = mock_data[symbol]
            price = response["Global Quote"].get("05. price", "N/A")
            if price == "N/A":
                print(f"Error: Price for {symbol} is not available")
                return None
            return float(price)

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
    try:
        response = requests.get(url).json()
        if "Global Quote" not in response:
            print(f"Error: No 'Global Quote' found in response for {symbol}")
            return None
        price = response["Global Quote"].get("05. price", "N/A")
        if price == "N/A":
            print(f"Error: Price for {symbol} is not available")
            return None
        return float(price)
    except Exception as e:
        print(f"Error fetching price for {symbol}: {e}")
        return None

# Helper function to calculate ROI
def calculate_roi(amount, purchase_price, current_price):
    total_purchase = amount * purchase_price
    total_current = amount * current_price
    return round(((total_current - total_purchase) / total_purchase) * 100, 2)

# Helper function to calculate total portfolio value
def calculate_total_value():
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, amount, price FROM portfolio")
    rows = cursor.fetchall()

    total_value = 0
    for row in rows:
        name, amount, purchase_price = row
        current_price = get_current_price(name)
        if current_price:
            total_value += current_price * amount

    conn.close()
    return total_value

# Helper function to calculate diversification index
def calculate_diversification():
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, amount, price FROM portfolio")
    rows = cursor.fetchall()

    total_value = calculate_total_value()
    diversification = []
    for row in rows:
        name, amount, purchase_price = row
        current_price = get_current_price(name)
        if current_price:
            asset_value = current_price * amount
            diversification.append({
                "name": name,
                "percentage": round((asset_value / total_value) * 100, 2)
            })

    conn.close()
    return diversification

@app.route("/")
def index():
    return render_template("index.html")

def calculate_total_value(portfolio_data):
    return sum([stock['total_value'] for stock in portfolio_data if stock['total_value'] != "N/A"])

def calculate_portfolio_roi(portfolio_data):
    total_purchase_value = sum([stock['amount'] * stock['purchase_price'] for stock in portfolio_data if stock['purchase_price'] != "N/A"])
    total_current_value = sum([stock['total_value'] for stock in portfolio_data if stock['total_value'] != "N/A"])

    if total_purchase_value == 0:
        return 0
    return round(((total_current_value - total_purchase_value) / total_purchase_value) * 100, 2)

def calculate_diversification_index(portfolio_data):
    total_value = sum([stock['total_value'] for stock in portfolio_data if stock['total_value'] != "N/A"])
    diversification_index = []

    for stock in portfolio_data:
        if stock['total_value'] != "N/A":
            diversification_index.append(stock['total_value'] / total_value * 100)

    if not diversification_index:
        return 0

    mean_diversification = sum(diversification_index) / len(diversification_index)
    squared_diff = sum([(x - mean_diversification) ** 2 for x in diversification_index])
    return round((squared_diff / len(diversification_index)) ** 0.5, 2)

@app.route("/portfolio", methods=["GET", "POST"])
def portfolio():
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()

    if request.method == "POST":
        try:
            name = request.form.get("name")
            amount = float(request.form.get("amount"))
            price = float(request.form.get("price"))

            cursor.execute("INSERT INTO portfolio (name, amount, price) VALUES (?, ?, ?)", (name, amount, price))
            conn.commit()
        except Exception as e:
            return f"An error occurred: {e}"

    cursor.execute("SELECT * FROM portfolio")
    rows = cursor.fetchall()

    # Fetch current prices and calculate ROI
    portfolio_data = []
    for row in rows:
        stock_id, name, amount, purchase_price = row
        current_price = get_current_price(name)
        if current_price is not None:
            roi = calculate_roi(amount, purchase_price, current_price)
            total_value = round(amount * current_price, 2)
            portfolio_data.append({
                "id": stock_id,
                "name": name,
                "amount": amount,
                "purchase_price": purchase_price,
                "current_price": current_price,
                "roi": roi,
                "total_value": total_value
            })
        else:
            portfolio_data.append({
                "id": stock_id,
                "name": name,
                "amount": amount,
                "purchase_price": purchase_price,
                "current_price": "N/A",
                "roi": "N/A",
                "total_value": "N/A"
            })

    total_value = calculate_total_value(portfolio_data)
    portfolio_roi = calculate_portfolio_roi(portfolio_data)
    diversification_index = calculate_diversification_index(portfolio_data)

    conn.close()

    return render_template("portfolio.html", portfolio=portfolio_data, total_value=total_value, portfolio_roi=portfolio_roi, diversification_index=diversification_index)


@app.route("/delete/<int:stock_id>", methods=["POST"])
def delete_stock(stock_id):
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM portfolio WHERE id = ?", (stock_id,))
    conn.commit()
    conn.close()

    return redirect(url_for("portfolio"))

if __name__ == "__main__":
    app.run(debug=True)
