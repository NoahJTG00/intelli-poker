from flask import Blueprint, request, render_template, redirect, url_for
import subprocess
import os

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

