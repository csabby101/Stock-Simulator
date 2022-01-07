import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    rows = db.execute("SELECT * FROM purchases WHERE userid = ?", session["user_id"])
    # print("rows print kar rha")
    # print(rows)
    # print(len(rows))
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
    format(cash, '.2f')

    bigtotal = cash

    if len(rows) > 0:
        for row in rows:
            prices = lookup(row['symbol'])
            # print("prices print kar rha")
            # print(prices)
            row['price'] = (prices["price"])
            totall = float(row['shares']) * row['price']
            bigtotal = bigtotal + totall
            row['total'] = totall
            row['name'] = (prices["name"])
            # print(row)

    return render_template("index.html", rows=rows, cash=cash, bigtotal=bigtotal)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        detail = lookup(symbol)

        if not symbol or detail == None:
            return apology("must provide correct symbol", 400)

        shares = request.form.get("shares")

        if not shares.isdigit():
            return apology("enter a positive integer")

        if not int(shares) > 0:
            return apology("enter a positive integer")

        price = detail["price"]
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]

        amount = price * float(shares)
        newcash = cash - amount
        bought = "bought"
        if amount <= cash:

            db.execute("INSERT into transactions (userid, shares, symbol, price, type) VALUES (?, ?, ?, ?, ?)",
                       session["user_id"], shares, symbol, amount, bought)

            preshares = db.execute("SELECT shares FROM purchases WHERE symbol = ? and userid = ?", symbol, session["user_id"])
            if len(preshares) != 0 and preshares[0]["shares"] > 0:
                # print(preshares)
                oldshares = int(preshares[0]["shares"])
                # print(oldshares)
                newshares = int(shares) + oldshares
                db.execute("UPDATE purchases SET shares = ? WHERE userid = ?", newshares, session["user_id"])
            else:
                db.execute("INSERT into purchases (userid, shares, symbol) VALUES (?, ?, ?)", session["user_id"], shares, symbol)

            db.execute("UPDATE users SET cash = ? where id = ?", newcash, session["user_id"])
            flash("You bought the stocks.")
        else:
            return apology("Cash not enough for making the purchase")

        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    rows = db.execute("SELECT * FROM transactions WHERE userid = ?", session["user_id"])

    return render_template("history.html", rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":
        symbol = request.form.get("symbol")
        detail = lookup(symbol)

        if not symbol or detail == None:
            return apology("must provide correct symbol", 400)

        name = detail["name"]
        price = detail["price"]
        return render_template("quoted.html", name=name, price=price)

    else:
        return render_template("quote.html")


@app.route("/addmoney", methods=["GET", "POST"])
@login_required
def addmoney():
    if request.method == "POST":
        amount = request.form.get("amount")
        cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
        newcash = cash + int(amount)
        db.execute("UPDATE users SET cash = ? where id = ?", newcash, session["user_id"])
        flash("Cash added successfully.")

        return redirect("/")

    else:
        return render_template("addmoney.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        if len(rows) == 1:
            return apology("username already taken", 400)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match", 400)

        username = request.form.get("username")
        password = request.form.get("password")
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, generate_password_hash(password))

        # Redirect user to login page
        return render_template("login.html")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("Please select a symbol")

        detail = lookup(symbol)

        shares = request.form.get("shares")
        # print(shares)
        ashares = db.execute("SELECT shares FROM purchases WHERE userid = ? AND symbol = ?",
                             session["user_id"], symbol)[0]["shares"]
        # print(ashares)
        if int(shares) > int(ashares):
            return apology("Not enough shares available for this symbol")

        else:
            price = detail["price"]
            amount = price * float(shares)

            cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])[0]["cash"]
            newcash = cash + amount

            db.execute("UPDATE users SET cash = ? where id = ?", newcash, session["user_id"])
            flash("You sold the stocks.")

            sold = "sold"
            db.execute("INSERT into transactions (userid, shares, symbol, price, type) VALUES (?, ?, ?, ?, ?)",
                       session["user_id"], shares, symbol, amount, sold)

            postshares = int(ashares) - int(shares)
            db.execute("UPDATE purchases SET shares = ? WHERE userid = ? AND symbol = ?", postshares, session["user_id"], symbol)

        return redirect("/")

    else:
        symbols = db.execute("SELECT symbol FROM purchases WHERE userid = ?", session["user_id"])
        return render_template("sell.html", symbols=symbols)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
