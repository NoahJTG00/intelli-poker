from configparser import Error
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
hand_history_data = []
# Existing routes ...

@game_bp.route('/hand_history', methods=['POST'])
def update_hand_history():
    global hand_history_data
    hand_history_data = request.json.get('hand_history', [])
    return jsonify({'status': 'success'})

# New route to serve hand history data
@game_bp.route('/get_hand_history', methods=['GET'])
def get_hand_history():
    return jsonify({'hand_history': hand_history_data})

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
    start_game() 
    sleep(2)
    return render_template('game.html')  

# New profile route
@game_bp.route('/instructions')
def instructions():
    return render_template('instructions.html')

@game_bp.route('/profile')
def profile():
    return render_template('profile.html')

@game_bp.route('/increment_progress', methods=['POST'])
def increment_progress():
    if 'username' not in session:
        return jsonify({"error": "User not logged in"}), 401

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        # Increment the progress for the "Play consecutive games" achievement
        cur.execute("UPDATE users SET play_consecutive_games = play_consecutive_games + 1 WHERE username = %s", (session['username'],))
        conn.commit()
        return jsonify({"message": "Progress incremented"})
    except Error as e:
        print(e)
        return jsonify({"error": "Failed to increment progress"}), 500
    finally:
        cur.close()
        conn.close()

@game_bp.route('/get_profile', methods=['GET'])
def get_profile():
    if 'username' not in session:
        return jsonify({"error": "User not logged in"}), 401

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT skill_level, personal_notes, play_consecutive_games FROM users WHERE username = %s", (session['username'],))
        user_profile = cur.fetchone()
        if user_profile:
            return jsonify(user_profile)
        return jsonify({"skill_level": "", "personal_notes": "", "play_consecutive_games": 0})
    except Error as e:
        print(e)
        return jsonify({"error": "Failed to fetch profile"}), 500
    finally:
        cur.close()
        conn.close()


@game_bp.route('/save_profile', methods=['POST'])
def save_profile():
    data = request.get_json()
    skill_level = data.get('skillLevel')
    player_notes = data.get('playerNotes')
    # helpful for debugging
    #print("Skill Level:", skill_level)
    #print("Player Notes:", player_notes)
    return jsonify({"message": "Profile saved successfully!"})


@game_bp.route("/logout", methods=['POST'])
def logout():
    # Your logout logic here
    session.clear()
    return redirect(url_for('game_bp.login'))