from flask import Blueprint, render_template, redirect, url_for

main_bp = Blueprint('main_bp', __name__)

@main_bp.route('/')
def index():
    return render_template("start_game.html") # Redirect to the start game page
