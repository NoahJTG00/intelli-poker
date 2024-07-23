from flask import Blueprint, render_template, redirect, url_for, session

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    if 'logged_in' in session and session['logged_in']:
        return render_template('index.html')
    else:
        return redirect(url_for('game_bp.login'))
