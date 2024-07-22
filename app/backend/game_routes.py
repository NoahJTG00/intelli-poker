from flask import Blueprint, request, render_template, redirect, url_for
import subprocess
import os
import socket

game_bp = Blueprint('game_bp', __name__)

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

@game_bp.route('/game/start', methods=['GET', 'POST'])
def start_game():
    if not is_server_running('127.0.0.1', 8000):
        start_server()
    return '', 204

@game_bp.route('/game', methods=['GET'])
def play_game():
    start_game()  # Starts the server if not running
    return render_template('game.html')  # Renders the game page
