from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user
import subprocess
import os
from . import bcrypt
from flask_bcrypt import Bcrypt
from time import sleep
from .utils import get_db_connection
import socket

game_bp = Blueprint('game_bp', __name__)

# Existing routes ...

@game_bp.route('/start', methods=['GET', 'POST'])
def start_game():
    if not is_server_running('127.0.0.1', 8000):
        start_server()
        return jsonify({'status': 'Server started'}), 200
    return jsonify({'status': 'Server already running'}), 200

def is_server_running(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        result = sock.connect_ex((host, port))
        return result == 0

def start_server():
    # Path to the separate virtual environment's python executable
    poker_env_python = os.path.join(os.path.abspath('venv'), 'bin', 'python')

    # Start the PyPokerGUI server using the separate virtual environment
    try:
        subprocess.Popen([poker_env_python, "-m", "pypokergui", "serve", "app/backend/game/poker_conf.yaml", "--port", "8000", "--speed", "moderate"])
    except Exception as e:
        print(f"Failed to start server: {e}")

@game_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        print(f"Received data - Username: {username}, Email: {email}, Password: {password}")

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
            conn.commit()
            flash('You are now registered and can log in', 'success')
            return redirect(url_for('game_bp.login'))
        except Exception as e:
            flash(f'Error: {e}', 'danger')
        finally:
            cur.close()
            conn.close()

    return render_template('register.html')

@game_bp.route('/login', methods=['GET', 'POST'])
def login():
    if "logged_in" in session:
        return redirect(url_for('main_bp.index'))
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
                return redirect(url_for('main_bp.index'))
            else:
                flash("Invalid login credentials", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template("login.html")

@game_bp.route('/game', methods=['GET'])
def play_game():
    start_game()  # Starts the server if not running
    sleep(2)
    return render_template('game.html')  # Renders the game page

# New profile route
@game_bp.route('/instructions')
def instructions():
    return render_template('instructions.html')

@game_bp.route('/profile')
def profile():
    return render_template('profile.html')


@game_bp.route("/logout", methods=['POST'])
def logout():
    # Your logout logic here
    session.clear()
    return redirect(url_for('game_bp.login'))