from configparser import Error
from datetime import datetime
from sqlite3 import Date
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
        print("------hHHEREH-----", flush=True)
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

@game_bp.route('/log_game_completion', methods=['POST'])
def log_game_completion():
    if 'username' not in session:
        return jsonify({"error": "User not logged in"}), 401

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT daily_streak, last_play_date FROM users WHERE username = %s", (session['username'],))
        user = cur.fetchone()
        if user:
            last_play_date = user['last_play_date']
            current_date = datetime.now().date()

            if last_play_date is None or (current_date - last_play_date).days > 1:
                # If more than a day has passed since the last play, reset the streak
                cur.execute("UPDATE users SET daily_streak = 1, last_play_date = %s WHERE username = %s", (current_date, session['username']))
            elif (current_date - last_play_date).days == 1:
                # If the user played yesterday, increment the streak
                new_streak = user['daily_streak'] + 1
                cur.execute("UPDATE users SET daily_streak = %s, last_play_date = %s WHERE username = %s", (new_streak, current_date, session['username']))
            else:
                # If the user played today already, do nothing
                pass
            conn.commit()
            return jsonify({"message": "Game logged successfully", "daily_streak": new_streak})
        return jsonify({"error": "User not found"}), 404
    except Error as e:
        print(e)
        return jsonify({"error": "Failed to log game completion"}), 500
    finally:
        cur.close()
        conn.close()

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
        cur.execute("SELECT play_consecutive_games, overachiever_notified FROM users WHERE username = %s", (session['username'],))
        user = cur.fetchone()

        if user:        
            new_count = user['play_consecutive_games'] + 1
            overachiever_notified = user['overachiever_notified']

            cur.execute("UPDATE users SET play_consecutive_games = %s WHERE username = %s", (new_count, session['username']))

            if new_count == 3 and not overachiever_notified:
                cur.execute("UPDATE users SET overachiever_notified = TRUE WHERE username = %s", (session['username'],))
            conn.commit()
            return jsonify({"message": "Progress incremented", "play_consecutive_games": new_count, "overachiever_notified": new_count == 3 and not overachiever_notified})
        return jsonify({"error": "User not found"}), 404
    except Error as e:
        print(e)
        return jsonify({"error": "Failed to increment progress"}), 500
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

@game_bp.route('/reset_progress', methods=['POST'])
def reset_progress():
    if 'username' not in session:
        return jsonify({"error": "User not logged in"}), 401

    data = request.get_json()
    try:
        reset_value = int(data.get('reset_value', 0))  # Convert to int, default to 0 if not provided
    except ValueError:
        return jsonify({"error": "Invalid reset value"}), 400  

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("UPDATE users SET play_consecutive_games = %s WHERE username = %s", (reset_value, session['username']))
        conn.commit()
        return jsonify({"message": "Progress reset successfully", "new_value": reset_value})
    except Error as e:
        print(e)
        return jsonify({"error": "Failed to reset progress"}), 500
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
        cur.execute("SELECT skill_level, personal_notes, play_consecutive_games, created_at, first_profile_visit, daily_streak, overachiever_notified FROM users WHERE username = %s", (session['username'],))
        user_profile = cur.fetchone()
        if user_profile:
            created_at = user_profile['created_at']
            account_age_days = (datetime.now() - created_at).days
            user_profile['account_age_days'] = account_age_days

            # Determine the award based on account age
            if account_age_days >= 365:
                user_profile['account_age_award'] = 'Veteran'
            elif account_age_days >= 2:
                user_profile['account_age_award'] = 'Seasoned'
            elif account_age_days >= 1:
                user_profile['account_age_award'] = 'Regular'
            else:
                user_profile['account_age_award'] = 'Newbie'
            
            first_visit = user_profile.get('first_profile_visit', True)
            if first_visit:
                # Update the database to mark the first visit as completed
                cur.execute("UPDATE users SET first_profile_visit = FALSE WHERE username = %s", (session['username'],))
                conn.commit()
                user_profile['first_profile_visit'] = True
            else:
                user_profile['first_profile_visit'] = False

            #print(user_profile) 
            return jsonify(user_profile)
        #print("Default profile returned")  # Debugging statement
        return jsonify({"skill_level": "", "personal_notes": "", "play_consecutive_games": 0, "account_age_days": 0, "account_age_award": "Newbie", "first_profile_visit": False, "daily_streak": 0, "overachiever_notified": False})
    except Error as e:
        print(e)
        return jsonify({"error": "Failed to fetch profile"}), 500
    finally:
        cur.close()
        conn.close()