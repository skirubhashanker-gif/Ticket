from __future__ import annotations

import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "ticket_system.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-change-me"


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(_: Any) -> None:
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db() -> None:
    db = get_db()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','user','tech')),
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('software','hardware')),
            status TEXT NOT NULL CHECK(status IN ('open','in_progress','pending_user','resolved','closed')),
            created_by INTEGER NOT NULL,
            assigned_to INTEGER,
            closing_comment TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY(created_by) REFERENCES users(id),
            FOREIGN KEY(assigned_to) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id INTEGER NOT NULL,
            sender_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(ticket_id) REFERENCES tickets(id),
            FOREIGN KEY(sender_id) REFERENCES users(id)
        );
        """
    )
    db.commit()


@app.before_request
def bootstrap() -> None:
    init_db()


@app.context_processor
def inject_user() -> dict[str, Any]:
    user = None
    if session.get("user_id"):
        user = get_db().execute(
            "SELECT id, username, role FROM users WHERE id = ?", (session["user_id"],)
        ).fetchone()
    return {"current_user": user}


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return wrapper


def role_required(*roles: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if user is None:
                return redirect(url_for("login"))
            if user["role"] not in roles:
                flash("You do not have permission for this action.", "error")
                return redirect(url_for("dashboard"))
            return func(*args, **kwargs)

        return wrapper

    return decorator


def get_current_user() -> sqlite3.Row | None:
    if not session.get("user_id"):
        return None
    return get_db().execute(
        "SELECT id, username, role FROM users WHERE id = ?", (session["user_id"],)
    ).fetchone()


def now_ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


@app.route("/")
def index():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register-admin", methods=["GET", "POST"])
def register_admin():
    db = get_db()
    admin_exists = db.execute("SELECT 1 FROM users WHERE role='admin' LIMIT 1").fetchone()
    if admin_exists:
        return redirect(url_for("login"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        if not username or not password:
            flash("Username and password are required.", "error")
        else:
            db.execute(
                "INSERT INTO users(username, password_hash, role, created_at) VALUES(?,?,?,?)",
                (username, generate_password_hash(password), "admin", now_ts()),
            )
            db.commit()
            flash("Admin created. Please log in.", "success")
            return redirect(url_for("login"))
    return render_template("register_admin.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    db = get_db()
    admin_exists = db.execute("SELECT 1 FROM users WHERE role='admin' LIMIT 1").fetchone()
    if not admin_exists:
        return redirect(url_for("register_admin"))

    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        user = db.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid credentials.", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = get_current_user()
    db = get_db()

    if user["role"] == "admin":
        stats = {
            "users": db.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"],
            "tickets": db.execute("SELECT COUNT(*) AS c FROM tickets").fetchone()["c"],
            "open_tickets": db.execute(
                "SELECT COUNT(*) AS c FROM tickets WHERE status IN ('open','in_progress','pending_user')"
            ).fetchone()["c"],
            "closed_tickets": db.execute(
                "SELECT COUNT(*) AS c FROM tickets WHERE status IN ('resolved','closed')"
            ).fetchone()["c"],
        }
        return render_template("dashboard_admin.html", stats=stats)

    if user["role"] == "tech":
        tickets = db.execute(
            """
            SELECT t.*, u.username AS created_by_name, tech.username AS assigned_to_name
            FROM tickets t
            JOIN users u ON u.id=t.created_by
            LEFT JOIN users tech ON tech.id=t.assigned_to
            ORDER BY t.updated_at DESC
            """
        ).fetchall()
        return render_template("dashboard_tech.html", tickets=tickets)

    tickets = db.execute(
        """
        SELECT t.*, tech.username AS assigned_to_name
        FROM tickets t
        LEFT JOIN users tech ON tech.id=t.assigned_to
        WHERE t.created_by=?
        ORDER BY t.updated_at DESC
        """,
        (user["id"],),
    ).fetchall()
    return render_template("dashboard_user.html", tickets=tickets)


@app.route("/users", methods=["GET", "POST"])
@login_required
@role_required("admin")
def manage_users():
    db = get_db()
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        role = request.form["role"].strip()
        if role not in {"user", "tech", "admin"}:
            flash("Invalid role.", "error")
        elif not username or not password:
            flash("Username and password are required.", "error")
        else:
            try:
                db.execute(
                    "INSERT INTO users(username, password_hash, role, created_at) VALUES(?,?,?,?)",
                    (username, generate_password_hash(password), role, now_ts()),
                )
                db.commit()
                flash("User created.", "success")
            except sqlite3.IntegrityError:
                flash("Username already exists.", "error")
    users = db.execute("SELECT id, username, role, created_at FROM users ORDER BY id DESC").fetchall()
    return render_template("users.html", users=users)


@app.route("/tickets/new", methods=["GET", "POST"])
@login_required
@role_required("user")
def new_ticket():
    if request.method == "POST":
        title = request.form["title"].strip()
        description = request.form["description"].strip()
        category = request.form["category"].strip()
        if category not in {"software", "hardware"}:
            flash("Invalid category.", "error")
        elif not title or not description:
            flash("Title and description are required.", "error")
        else:
            db = get_db()
            db.execute(
                """
                INSERT INTO tickets(title, description, category, status, created_by, created_at, updated_at)
                VALUES(?,?,?,?,?,?,?)
                """,
                (title, description, category, "open", session["user_id"], now_ts(), now_ts()),
            )
            db.commit()
            flash("Ticket created successfully.", "success")
            return redirect(url_for("dashboard"))
    return render_template("new_ticket.html")


@app.route("/tickets/<int:ticket_id>", methods=["GET", "POST"])
@login_required
def ticket_detail(ticket_id: int):
    db = get_db()
    user = get_current_user()
    ticket = db.execute(
        """
        SELECT t.*, creator.username AS creator_name, tech.username AS assigned_to_name
        FROM tickets t
        JOIN users creator ON creator.id=t.created_by
        LEFT JOIN users tech ON tech.id=t.assigned_to
        WHERE t.id=?
        """,
        (ticket_id,),
    ).fetchone()

    if not ticket:
        flash("Ticket not found.", "error")
        return redirect(url_for("dashboard"))

    if user["role"] == "user" and ticket["created_by"] != user["id"]:
        flash("You can only access your own tickets.", "error")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        action = request.form.get("action", "")

        if action == "update_ticket" and user["role"] in {"tech", "admin"}:
            status = request.form.get("status", "")
            assigned_to = request.form.get("assigned_to")
            closing_comment = request.form.get("closing_comment", "").strip() or None
            if status not in {"open", "in_progress", "pending_user", "resolved", "closed"}:
                flash("Invalid status.", "error")
            else:
                assigned_user_id = int(assigned_to) if assigned_to else None
                db.execute(
                    """
                    UPDATE tickets
                    SET status=?, assigned_to=?, closing_comment=?, updated_at=?
                    WHERE id=?
                    """,
                    (status, assigned_user_id, closing_comment, now_ts(), ticket_id),
                )
                db.commit()
                flash("Ticket updated.", "success")
                return redirect(url_for("ticket_detail", ticket_id=ticket_id))

        if action == "send_message":
            message = request.form.get("message", "").strip()
            if message:
                db.execute(
                    "INSERT INTO messages(ticket_id, sender_id, message, created_at) VALUES(?,?,?,?)",
                    (ticket_id, user["id"], message, now_ts()),
                )
                db.commit()
                flash("Message sent.", "success")
                return redirect(url_for("ticket_detail", ticket_id=ticket_id))
            flash("Message cannot be empty.", "error")

    tech_users = db.execute("SELECT id, username FROM users WHERE role='tech' ORDER BY username").fetchall()
    messages = db.execute(
        """
        SELECT m.*, u.username AS sender_name, u.role AS sender_role
        FROM messages m
        JOIN users u ON u.id=m.sender_id
        WHERE m.ticket_id=?
        ORDER BY m.created_at ASC
        """,
        (ticket_id,),
    ).fetchall()

    return render_template(
        "ticket_detail.html",
        ticket=ticket,
        tech_users=tech_users,
        messages=messages,
        can_update=user["role"] in {"tech", "admin"},
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
