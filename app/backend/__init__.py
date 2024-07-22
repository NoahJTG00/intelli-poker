import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
import openai
import logging

load_dotenv()

bcrypt = Bcrypt()

# Set your OpenAI API key here
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

analysis_list = []
def create_app():
    app = Flask(__name__, template_folder="../frontend/templates", static_folder="../frontend/static")
    app.secret_key = os.urandom(24)

    app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

    bcrypt.init_app(app)

    from app.backend.routes import main_bp
    app.register_blueprint(main_bp)

    from app.backend.game_routes import game_bp
    app.register_blueprint(game_bp)

    @app.route('/chat', methods=['POST'])
    def chat():
        data = request.get_json()
        cards = data.get('cards')
        game_state = data.get('game_state')

        response = openai.chat.completions.create(
             model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a poker expert providing Game Theory Optimal (GTO) analysis."},
        {"role": "user", "content": f"""You are playing in a 6-handed Texas Hold'em game. Here is the current game state:

        {game_state}

        Your Cards: {cards}

        Tell the user if thay made the right decision or not. Then give a 3 medium sentence max analysis of their decision and whether it was the right or wrong one."""}
            ]
        )

        response_text = response.choices[0].message.content

        return jsonify({'response': response_text})

    @app.route('/analysis', methods=['POST'])
    def add_analysis():
        data = request.get_json()
        analysis = data.get('analysis')
        if analysis:
            analysis_list.append(analysis)
        return '', 204

    @app.route('/get_analysis', methods=['GET'])
    def get_analysis():
        return jsonify({'analysis_list': analysis_list})

    return app

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = create_app()
    app.run()
