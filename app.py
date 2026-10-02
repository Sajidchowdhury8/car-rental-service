from flask import Flask
import sqlite3

app = Flask(__name__)


def get_db():
    connection = sqlite3.connect("rental.db")
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            category TEXT NOT NULL,
            price_per_day REAL NOT NULL,
            available INTEGER NOT NULL
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            car_id INTEGER NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (car_id) REFERENCES cars(id)
        )
    """)

    car_count = db.execute(
        "SELECT COUNT(*) FROM cars"
    ).fetchone()[0]

    if car_count == 0:
        cars = [
            ("Toyota", "Camry", "Sedan", 55.00, 1),
            ("Honda", "CR-V", "SUV", 70.00, 1),
            ("Nissan", "Sentra", "Economy", 45.00, 1),
            ("Ford", "Explorer", "SUV", 85.00, 1)
        ]

        db.executemany("""
            INSERT INTO cars
            (make, model, category, price_per_day, available)
            VALUES (?, ?, ?, ?, ?)
        """, cars)

    db.commit()
    db.close()


@app.route("/")
def home():
    return "<h1>Car Rental Service</h1><p>Prototype is running successfully.</p>"

@app.route("/register", methods=["GET", "POST"])
def register():
    return "Registration page coming soon"


@app.route("/login", methods=["GET", "POST"])
def login():
    return "Login page coming soon"


@app.route("/cars")
def cars():
    return "Cars page coming soon"


@app.route("/book/<int:car_id>", methods=["GET", "POST"])
def book(car_id):
    return f"Booking page for car {car_id} coming soon"

if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)