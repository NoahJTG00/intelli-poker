import os
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


# Initialize the OpenAI API client
client = OpenAI(
    # This is the default and can be omitted
    api_key = os.getenv("OPENAI_API_KEY"),
)

def get_poker_gto_analysis(game_state, cards):
    """
    Call the OpenAI API to get Poker GTO analysis on the given game state and decision.

    Parameters:
        game_state (str): A description of the current game state.
        cards (str): The cards held by the player.

    Returns:
        str: The GTO analysis provided by the AI model.
    """
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a poker expert providing Game Theory Optimal (GTO) analysis."},
            {"role": "user", "content": f"You are playing 6-handed and the players information shows who is in the SB and the BB and is in correct order after that, therefore infer your position from the list. Analyze the following game state given your cards:\n\nYour Cards:\n{cards}\n\n and the Game State:\n{game_state}\n\nProvide a simplified GTO analysis of the decision I just made:"}
        ],
        model="gpt-4o",
    )

    # Extract the analysis from the API response
    return chat_completion.choices[0].message.content