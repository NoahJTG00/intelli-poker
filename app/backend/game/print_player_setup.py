import pypokerengine.utils.visualize_utils as U
from pypokerengine.players import BasePokerPlayer
from pypokerengine.engine.player import Player

import requests
import json

class FishPlayer(BasePokerPlayer):

    GAME_STATE = ""
    HOLE_CARDS = ""
    HAND_HISTORY = []
    
    def declare_action(self, valid_actions, hole_card, round_state):
        self.get_hole_cards(round_state)
        call_action_info = valid_actions[1]
        action, amount = call_action_info["action"], call_action_info["amount"]
        return action, amount

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        stage = street.capitalize()
        self.HAND_HISTORY.append(f"--- {stage} ---")
        self.send_hand_history_to_frontend()
        if len(self.GAME_STATE) > 5:
            analysis = self.get_hand_analysis(self.GAME_STATE, self.HOLE_CARDS)
            print(f'Analysis:\n{analysis}\n\n', flush=True)
            self.send_analysis_to_frontend(analysis)

    def receive_game_update_message(self, action, round_state):
        self.GAME_STATE = U.visualize_game_update(action, round_state, self.uuid)
        # Simplified action logging
        player_name = self.get_player_name(action['player_uuid'], round_state['seats'])
        action_string = self.format_action(action, player_name)
        self.HAND_HISTORY.append(action_string)
        self.send_hand_history_to_frontend()
    
    def get_player_name(self, uuid, seats):
        for player in seats:
            if player['uuid'] == uuid:
                return player['name']
        return "Unknown"

    def format_action(self, action, player_name):
        action_type = action['action'].lower()
        if action_type == 'fold':
            return f"{player_name} folded"
        elif action_type == 'call':
            return f"{player_name} called"
        elif action_type == 'raise':
            return f"{player_name} raised ${action['amount']}"
        elif action_type == 'bet':
            return f"{player_name} bet ${action['amount']}"
        return f"{player_name} performed an unknown action"

    def send_hand_history_to_frontend(self):
        url = 'http://127.0.0.1:5000/hand_history'
        headers = {'Content-Type': 'application/json'}
        payload = {'hand_history': self.HAND_HISTORY}
        requests.post(url, headers=headers, data=json.dumps(payload))
    
    def receive_round_result_message(self, winners, hand_info, round_state):
        self.HAND_HISTORY = []
        self.send_hand_history_to_frontend()

    def get_hole_cards(self, round_state):
        for uuid, cards in Player.hole_cards_dict.items():
            name = next((seat['name'] for seat in round_state['seats'] if seat['uuid'] == uuid), "Unknown")
            player_type = "human_player" if "human" in name else "fish_player"
            if player_type == "human_player":
                self.HOLE_CARDS = ' '.join(str(card) for card in cards)
            if not len(uuid) == 1:
                self.HOLE_CARDS = ' '.join(str(card) for card in cards)

    def get_hand_analysis(self, game_state, hole_cards):
        url = 'http://127.0.0.1:5000/chat'  # Update with your Flask server URL if different
        headers = {'Content-Type': 'application/json'}
        payload = {
            'cards': hole_cards,
            'game_state': game_state
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        if response.status_code == 200:
            return response.json().get('response', 'No analysis available.')
        else:
            return f'Error: {response.status_code}'

    def send_analysis_to_frontend(self, analysis):
        url = 'http://127.0.0.1:5000/analysis'  # Endpoint to send analysis to the frontend
        headers = {'Content-Type': 'application/json'}
        payload = {'analysis': analysis}
        requests.post(url, headers=headers, data=json.dumps(payload))

def setup_ai():
    return FishPlayer()
