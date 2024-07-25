import os
from flask import Flask, session, redirect, url_for, render_template, request, flash, jsonify
from dotenv import load_dotenv
from flask_bcrypt import Bcrypt
import openai

load_dotenv()

bcrypt = Bcrypt()


# Set your OpenAI API key here
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY
print(OPENAI_API_KEY, flush=True)
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
        print(cards, flush=True)
        game_state = data.get('game_state')

        response = openai.chat.completions.create(
             model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a poker expert providing Game Theory Optimal (GTO) analysis."},
        {"role": "user", "content": f"""You are playing in a 6-handed Texas Hold'em game. Here is the current game state:

        {game_state}

        Your Cards: {cards}

        Tell the user if thay made the right decision or not. Then give a 3 medium sentence max analysis of their decision and whether it was the right or wrong one."""}
            ]
        )

        response_text = response.choices[0].message.content
        print(response_text, flush=True)
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
    
    @app.route('/ask_ai', methods=['POST'])
    def ask_ai():
        try:
            data = request.get_json()
            cards = data.get('cards')
            game_state = data.get('game_state')

            if not cards or not game_state:
                return jsonify({'error': 'Cards and game state are required.'}), 400

            response = openai.Completion.create(
                engine="gpt-4",
                prompt=f"You are a poker expert. Based on the following game state and player's cards, provide a hint for what the player should do next (call, fold, or raise):\n\nGame State: {game_state}\nPlayer's Cards: {cards}",
                max_tokens=100
            )

            response_text = response.choices[0].text.strip()
            return jsonify({'response': response_text})
        except Exception as e:
            print(f"Error: {e}", flush=True)
            return jsonify({'error': str(e)}), 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run()
    
