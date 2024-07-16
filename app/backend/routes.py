from flask import Blueprint, redirect, url_for

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    return redirect(url_for('game_bp.start_game'))  # Redirect to the start game page
