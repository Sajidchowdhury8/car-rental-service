from flask import Flask, request, redirect, render_template, session
import sqlite3

app = Flask(__name__)
app.secret_key = "car-rental-secret-key"


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
    return """
        <h1>Car Rental Service</h1>
        <p>Prototype is running successfully.</p>

        <a href="/register">Register</a>
        <br><br>
        <a href="/login">Login</a>
    """


@app.route("/register", methods=["GET", "POST"])
def register():
    message = None

    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        db = get_db()

        try:
            db.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, password)
            )
            db.commit()

        except sqlite3.IntegrityError:
            db.close()

            return render_template(
                "register.html",
                message="An account with that email already exists."
            )

        db.close()

        return redirect("/login")

    return render_template(
        "register.html",
        message=message
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    message = None

    if request.method == "POST":
        email = request.form["email"].strip()
        password = request.form["password"]

        db = get_db()

        user = db.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()

        db.close()

        if user:
            session["user_id"] = user["id"]

            return redirect("/cars")

        message = "Incorrect email or password."

    return render_template(
        "login.html",
        message=message
    )


@app.route("/cars")
def cars():

    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    cars_list = db.execute(
        "SELECT * FROM cars"
    ).fetchall()

    db.close()

    return render_template(
        "cars.html",
        cars=cars_list
    )


@app.route("/book/<int:car_id>", methods=["GET", "POST"])
def book(car_id):

    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    car = db.execute(
        "SELECT * FROM cars WHERE id = ?",
        (car_id,)
    ).fetchone()

    if car is None:
        db.close()

        return "Car not found.", 404

    if not car["available"]:
        db.close()

        return "This car is not available."

    if request.method == "POST":

        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        if end_date < start_date:
            db.close()

            return render_template(
                "booking.html",
                car=car,
                message="End date must be on or after the start date."
            )

        db.execute("""
            INSERT INTO bookings
            (user_id, car_id, start_date, end_date)

            VALUES (?, ?, ?, ?)
        """, (
            session["user_id"],
            car_id,
            start_date,
            end_date
        ))

        db.execute(
            "UPDATE cars SET available = 0 WHERE id = ?",
            (car_id,)
        )

        db.commit()
        db.close()

        return render_template(
            "confirmation.html",
            car=car,
            start_date=start_date,
            end_date=end_date
        )

    db.close()

    return render_template(
        "booking.html",
        car=car,
        message=None
    )


@app.route("/logout")
def logout():
    session.clear()

    return redirect("/login")


if __name__ == "__main__":
    initialize_database()
    app.run(debug=True)