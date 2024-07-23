from flask import Blueprint, request, render_template, redirect, url_for, flash, session
import subprocess
import os
from . import bcrypt
from .utils import get_db_connection


game_bp = Blueprint('game_bp', __name__, url_prefix='/game')

@game_bp.route('/start', methods=['GET', 'POST'])
def start_game():
    if request.method == 'POST':
        
        # Path to the separate virtual environment's python executable
        poker_env_python = os.path.join(os.path.abspath('venv'), 'bin', 'python')

        # Start the PyPokerGUI server using the separate virtual environment
        subprocess.Popen([poker_env_python, "-m", "pypokergui", "serve", "app/backend/game/poker_conf.yaml", "--port", "8000", "--speed", "moderate"])
        
        return '', 204
    return render_template('start_game.html')

@game_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
            conn.commit()
            flash('You are now registered and can log in', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        finally:
            cur.close()
            conn.close()

    return render_template('register.html')

@game_bp.route('/login', methods=['GET', 'POST'])
def login():
    if "logged_in" in session:
        return redirect(url_for('index'))
    if request.method == "POST":
        username = request.form["username"]
        password_candidate = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM users WHERE username = %s", [username])
            user = cur.fetchone()

            if user and bcrypt.check_password_hash(user["password"], password_candidate):
                session["logged_in"] = True
                session["username"] = user["username"]
                flash("You are now logged in", "success")
                return redirect(url_for('index'))
            else:
                flash("Invalid login credentials", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template("login.html")
    

